import pandas as pd
import datetime as dt
import numpy as np
import os
import yaml
import struct

def requires_assimilation_info(func):
    def wrapper(self, *args, **kwargs):
        if self.has_assimilation_info:
            return func(self, *args, **kwargs)
        else:
            raise ValueError("Assimilation information is required to call this function.")
    return wrapper

def requires_posterior_info(func):
    def wrapper(self, *args, **kwargs):
        if self.has_posterior_info:
            return func(self, *args, **kwargs)
        else:
            raise ValueError("Posterior information is required to call this function.")
    return wrapper


class obs_sequence:
    """Create an obs_sequence object from an ascii observation sequence file.

    Attributes:
        df (pandas.DataFrame): DataFrame containing all the observations.
        all_obs (list): List of all observations, each observation is a list.
        header (str): Header from the ascii file.
        vert (dict): Dictionary of dart vertical units.
        types (dict): Dictionary of types in the observation sequence file.
        copie_names (list): Names of copies in the observation sequence file.
            Spelled 'copie' to avoid conflict with the Python built-in copy function.
            Spaces are replaced with underscores in copie_names.
   
    Parameters:
        file : the input observation sequence ascii file

    Example: 
        Read the observation sequence from file:
            ``obs_seq = obs_sequence('/home/data/obs_seq.final.ascii.small')``
        Access the resulting pandas DataFrame:
            ``obs_seq.df``

    For 3D sphere models: latitude and longitude are in degrees in the DataFrame

    Calculations:
          
        - sq_err = (mean-obs)**2  
        - bias = (mean-obs)  
        - rmse = sqrt( sum((mean-obs)**2)/n )
        - bias = sum((mean-obs)/n)
        - spread = sum(sd)
        - totalspread = sqrt(sum(sd+obs_err_var)) 
        
    """
    ## static variables
    # vertrical coordinate:
    #   undefined 'VERTISUNDEF'
    #   surface 'VERTISSURFACE' (value is surface elevation in m)
    #   model level 'VERTISLEVEL'
    #   pressure 'VERTISPRESSURE' (in pascals)
    #   height 'VERTISHEIGHT' (in meters)
    #   scale height 'VERTISSCALEHEIGHT' (unitless)
    vert = {-2: 'undefined',              
            -1: 'surface (m)', 
             1: 'model level',
             2: 'pressure (Pa)',
             3: 'height (m)',
             4: 'scale height' }

    reversed_vert = {value: key for key, value in vert.items()}

    
    def __init__(self, file, synonyms=None):
        self.loc_mod = 'None'
        self.has_assimilation_info = False
        self.has_posterior = False
        self.file = file
        self.synonyms_for_obs = ['NCEP BUFR observation',
                                 'AIRS observation', 
                                 'GTSPP observation', 
                                 'SST observation',
                                 'observations',
                                 'WOD observation']
        if synonyms:
            if isinstance(synonyms, list):
                self.synonyms_for_obs.extend(synonyms)
            else:
                self.synonyms_for_obs.append(synonyms)

        if file is None:
            # Early exit for testing purposes
            self.df = pd.DataFrame()
            self.types = {}
            self.reverse_types = {}
            self.copie_names = []
            self.n_copies = 0
            self.seq = []
            self.all_obs = []
            return

        module_dir = os.path.dirname(__file__)
        self.default_composite_types = os.path.join(module_dir,"composite_types.yaml")

        if self.is_binary(file):
            self.header = self.read_binary_header(file)
        else:
            self.header = self.read_header(file)

        self.types = self.collect_obs_types(self.header)
        self.reverse_types = {v: k for k, v in self.types.items()}
        self.copie_names, self.n_copies = self.collect_copie_names(self.header)

        if self.is_binary(file):
            self.seq = self.obs_binary_reader(file, self.n_copies)
            self.loc_mod = 'loc3d'  # only loc3d supported for binary, & no way to check
        else:
            self.seq = self.obs_reader(file, self.n_copies)

        self.all_obs = self.create_all_obs() # uses up the generator
        # at this point you know if the seq is loc3d or loc1d
        if self.loc_mod == 'None':
            raise ValueError("Neither 'loc3d' nor 'loc1d' could be found in the observation sequence.")
        self.columns = self.column_headers()
        self.df = pd.DataFrame(self.all_obs, columns = self.columns)
        if self.loc_mod == 'loc3d':
            self.df['longitude'] = np.rad2deg(self.df['longitude'])
            self.df['latitude'] = np.rad2deg(self.df['latitude'])
        # rename 'X observation' to observation
        self.synonyms_for_obs = [synonym.replace(' ', '_') for synonym in self.synonyms_for_obs]
        rename_dict = {old: 'observation' for old in self.synonyms_for_obs  if old in self.df.columns}
        self.df = self.df.rename(columns=rename_dict)

        # calculate bias and sq_err is the obs_seq is an obs_seq.final
        if 'prior_ensemble_mean'.casefold() in map(str.casefold, self.columns):
            self.has_assimilation_info = True
            self.df['prior_bias'] = (self.df['prior_ensemble_mean'] - self.df['observation'])
            self.df['prior_sq_err'] = self.df['prior_bias']**2  # squared error
        if 'posterior_ensemble_mean'.casefold() in map(str.casefold, self.columns):
            self.has_posterior_info = True
            self.df['posterior_bias'] = (self.df['posterior_ensemble_mean'] - self.df['observation'])
            self.df['posterior_sq_err'] = self.df['posterior_bias']**2

    def create_all_obs(self):
        """ steps through the generator to create a
            list of all observations in the sequence 
        """
        all_obs = []
        for obs in self.seq:
            data = self.obs_to_list(obs)
            all_obs.append(data)
        return all_obs

    def obs_to_list(self, obs):
        """put single observation into a list

           discards obs_def
        """
        data = []
        data.append(obs[0].split()[1]) # obs_num
        data.extend(list(map(float,obs[1:self.n_copies+1]))) # all the copies
        data.append(obs[self.n_copies+1]) # linked list info
        try:  # HK todo only have to check loc3d or loc1d for the first observation, the whole file is the same
            locI = obs.index('loc3d')
            location = obs[locI+1].split()
            data.append(float(location[0]))  # location x
            data.append(float(location[1]))  # location y
            data.append(float(location[2]))  # location z
            data.append(obs_sequence.vert[int(location[3])])
            self.loc_mod = 'loc3d'
        except ValueError:
            try:
                locI = obs.index('loc1d')
                location = obs[locI+1]
                data.append(float(location))  # 1d location 
                self.loc_mod = 'loc1d'
            except ValueError:
                raise ValueError("Neither 'loc3d' nor 'loc1d' could be found in the observation sequence.")
        typeI = obs.index('kind') # type of observation
        type_value = obs[typeI + 1]
        if not self.types:
            data.append('Identity')
        else:
            data.append(self.types[type_value]) # observation type
            
        # any observation specific obs def info is between here and the end of the list
        # can be obs_def & external forward operator
        metadata = obs[typeI+2:-2]
        obs_def_metadata, external_metadata = self.split_metadata(metadata)
        data.append(obs_def_metadata)
        data.append(external_metadata)

        time = obs[-2].split()
        data.append(int(time[0])) # seconds
        data.append(int(time[1])) # days
        data.append(convert_dart_time(int(time[0]), int(time[1]))) # datetime   # HK todo what is approprate for 1d models?
        data.append(float(obs[-1])) # obs error variance ?convert to sd?

        return data

    @staticmethod
    def split_metadata(metadata):
        """
        Split the metadata list at the first occurrence of an element starting with 'externalF0'.

        Args:
            metadata (list of str): The metadata list to be split.

        Returns:
            tuple: Two sublists, the first containing elements before 'externalF0', and the second
                containing 'externalF0' and all elements after it. If 'externalF0' is not found,
                the first sublist contains the entire metadata list, and the second is empty.
        """
        for i, item in enumerate(metadata):
            if item.startswith('external_FO'):
                return metadata[:i], metadata[i:]
        return metadata, []

    def list_to_obs(self, data):
        obs = []
        obs.append('OBS        ' + str(data[0]))  # obs_num lots of space
        obs.extend(data[1:self.n_copies+1])  # all the copies
        obs.append(data[self.n_copies+1])  # linked list info
        obs.append('obdef')  # TODO HK: metadata obs_def 
        obs.append(self.loc_mod)
        if self.loc_mod == 'loc3d':
            obs.append('   '.join(map(str, data[self.n_copies+2:self.n_copies+5])) + '   ' + str(self.reversed_vert[data[self.n_copies+5]]) )  # location x, y, z, vert
            obs.append('kind') # this is type of observation
            obs.append(self.reverse_types[data[self.n_copies + 6]])  # observation type
            # Convert metadata to a string and append
            obs.extend(data[self.n_copies + 7])  # metadata
        elif self.loc_mod == 'loc1d':
            obs.append(data[self.n_copies+2])  # 1d location
            obs.append('kind') # this is type of observation
            obs.append(self.reverse_types[data[self.n_copies + 3]])  # observation type
            # Convert metadata to a string and append
            metadata = ' '.join(map(str, data[self.n_copies + 4:-4]))
            if metadata:
                obs.append(metadata)  # metadata
        obs.append(' '.join(map(str, data[-4:-2])))  # seconds, days
        obs.append(data[-1])  # obs error variance

        return obs

    @staticmethod
    def generate_linked_list_pattern(n):
        """Create a list of strings with the linked list pattern for n lines."""
        result = []
        for i in range(n-1):
            col1 = i if i > 0 else -1
            col2 = i + 2
            col3 = -1
            result.append(f"{col1:<12}{col2:<11}{col3}")
        result.append(f"{n-1:<12}{'-1':<11}{'-1'}")
        return result

    def write_obs_seq(self, file, df=None):
        """
        Write the observation sequence to a file.
        
        This function writes the observation sequence to disk. 
        If no DataFrame is provided, it writes the obs_sequence object to a file using the
        header and all observations stored in the object.
        If a DataFrame is provided,it creates a header and linked list from the DataFrame, 
        then writes the DataFrame obs to an obs_sequence file. Note the DataFrame is assumed
        to have been created from obs_sequence object.
        
        
        Parameters:
            file (str): The path to the file where the observation sequence will be written.
            df (pandas.DataFrame, optional): A DataFrame containing the observation data. If not provided, the function uses self.header and self.all_obs.
        
        Returns:
            None
        
        Examples:
            ``obs_seq.write_obs_seq('/path/to/output/file')``
            ``obs_seq.write_obs_seq('/path/to/output/file', df=obs_seq.df)``
        """
        with open(file, 'w') as f:
            
            if df is not None:
                # If a DataFrame is provided, update the header with the number of observations
                num_rows = len(df)
                replacement_string = f'num_obs: {num_rows:>10} max_num_obs: {num_rows:>10}'
                new_header = [replacement_string if 'num_obs' in element else element for element in self.header]

                for line in new_header[:-1]:
                    f.write(str(line) + '\n')
                first = 1
                f.write(f"first: {first:>12} last: {num_rows:>12}\n")

                # TODO HK is there something better than copying the whole thing here?
                df_copy = df.copy()  # copy since you want to change for writing. 
                # back to radians for obs_seq
                if self.loc_mod == 'loc3d':
                    df_copy['longitude'] = np.deg2rad(self.df['longitude'])
                    df_copy['latitude'] = np.deg2rad(self.df['latitude'])
                if 'bias' in df_copy.columns:
                    df_copy = df_copy.drop(columns=['bias', 'sq_err'])                
                
                # linked list for reading by dart programs
                df_copy = df_copy.sort_values(by=['time']) # sort the DataFrame by time
                df_copy['obs_num'] = df.index + 1 # obs_num in time order
                df_copy['linked_list'] = obs_sequence.generate_linked_list_pattern(len(df_copy)) # linked list pattern

                def write_row(row):
                    ob_write = self.list_to_obs(row.tolist())
                    for line in ob_write:
                        f.write(str(line) + '\n')
                
                df_copy.apply(write_row, axis=1)
  
            else:
                # If no DataFrame is provided, use self.header and self.all_obs
                for line in self.header:
                    f.write(str(line) + '\n')
                for obs in self.all_obs:
                    ob_write = self.list_to_obs(obs)
                    for line in ob_write:
                        f.write(str(line) + '\n')


    def column_headers(self):
        """define the columns for the dataframe """
        heading = []
        heading.append('obs_num')
        heading.extend(self.copie_names)
        heading.append('linked_list')
        if self.loc_mod == 'loc3d':
            heading.append('longitude')
            heading.append('latitude')
            heading.append('vertical')
            heading.append('vert_unit')
        elif self.loc_mod == 'loc1d':
            heading.append('location')
        heading.append('type')
        heading.append('metadata')
        heading.append('external_FO')
        heading.append('seconds')
        heading.append('days')
        heading.append('time')
        heading.append('obs_err_var')
        return heading

    @requires_assimilation_info    
    def select_by_dart_qc(self, dart_qc):
        """
        Selects rows from a DataFrame based on the DART quality control flag.

        Parameters:
            df (DataFrame): A pandas DataFrame.
            dart_qc (int): The DART quality control flag to select.

        Returns:
            DataFrame: A DataFrame containing only the rows with the specified DART quality control flag.

        Raises:
            ValueError: If the DART quality control flag is not present in the DataFrame.
        """
        if dart_qc not in self.df['DART_quality_control'].unique():
            raise ValueError(f"DART quality control flag '{dart_qc}' not found in DataFrame.")
        else:
            return self.df[self.df['DART_quality_control'] == dart_qc]

    @requires_assimilation_info
    def select_failed_qcs(self):
        """
        Select rows from the DataFrame where the DART quality control flag is greater than 0.

        Returns:
            pandas.DataFrame: A DataFrame containing only the rows with a DART quality control flag greater than 0.
        """
        return self.df[self.df['DART_quality_control'] > 0]

    @requires_assimilation_info
    def possible_vs_used(self):
        """
        Calculates the count of possible vs. used observations by type.

        This function takes a DataFrame containing observation data, including a 'type' column for the observation
        type and an 'observation' column. The number of used observations ('used'), is the total number
        minus the observations that failed quality control checks (as determined by the `select_failed_qcs` function).
        The result is a DataFrame with each observation type, the count of possible observations, and the count of
        used observations.

        Returns:
            pd.DataFrame: A DataFrame with three columns: 'type', 'possible', and 'used'. 'type' is the observation type,
            'possible' is the count of all observations of that type, and 'used' is the count of observations of that type
            that passed quality control checks.
        """
        possible = self.df.groupby('type')['observation'].count()
        possible.rename('possible', inplace=True)
        
        failed_qcs = self.select_failed_qcs().groupby('type')['observation'].count()
        used = possible - failed_qcs.reindex(possible.index, fill_value=0)
        used.rename('used', inplace=True)
        
        return pd.concat([possible, used], axis=1).reset_index()


    @staticmethod
    def is_binary(file):
        """Check if a file is binary file."""
        with open(file, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:
                return True
        return False


    @staticmethod
    def read_header(file):
        """Read the header and number of lines in the header of an ascii obs_seq file"""
        header = []
        with open(file, 'r') as f:
            for line in f:
                if "first:" in line and "last:" in line:
                    header.append(line.strip())
                    break
                else:
                    header.append(line.strip())
        return header

    @staticmethod
    def read_binary_header(file):
        """Read the header and number of lines in the header of a binary obs_seq file from Fortran output"""
        header = []
        linecount = 0
        obs_types_definitions = -1000
        num_obs = 0
        max_num_obs = 0 
        # need to get:
        #   number of obs_type_definitions
        #   number of copies
        #   number of qcs
        with open(file, 'rb') as f:
            while True:
                # Read the record length
                record_length = obs_sequence.read_record_length(f)
                if record_length is None:
                    break
                record = f.read(record_length)
                if not record: # end of file
                    break

                # Read the trailing record length (should match the leading one)
                obs_sequence.check_trailing_record_length(f, record_length)

                linecount += 1

                if linecount == 3: 
                    obs_types_definitions = struct.unpack('i', record)[0]
                    continue               

                if linecount == 4+obs_types_definitions:
                    num_copies, num_qcs, num_obs, max_num_obs = struct.unpack('iiii', record)[:16]
                    break
            
            # Go back to the beginning of the file
            f.seek(0)
            
            for _ in range(2):
                record_length = obs_sequence.read_record_length(f)
                if record_length is None:
                    break

                record = f.read(record_length)
                if not record:  # end of file
                    break

                obs_sequence.check_trailing_record_length(f, record_length)  
                header.append(record.decode('utf-8').strip())                          

            header.append(str(obs_types_definitions))

            # obs_types_definitions
            for _ in range(3,4+obs_types_definitions):
                 # Read the record length
                record_length = obs_sequence.read_record_length(f)
                if record_length is None:
                    break

                # Read the actual record
                record = f.read(record_length)
                if not record:  # end of file
                    break

                obs_sequence.check_trailing_record_length(f, record_length) 

                if _ == 3:
                    continue # num obs_types_definitions
                # Read an integer and a string from the record
                integer_value = struct.unpack('i', record[:4])[0]
                string_value = record[4:].decode('utf-8').strip()
                header.append(f"{integer_value} {string_value}")

            header.append(f"num_copies:   {num_copies}  num_qc:   {num_qcs}")
            header.append(f"num_obs: {num_obs}  max_num_obs: {max_num_obs}")
           
            #copie names
            for _ in range(5+obs_types_definitions, 5+obs_types_definitions+num_copies+num_qcs+1):
                 # Read the record length
                record_length = obs_sequence.read_record_length(f)
                if record_length is None:
                    break

                # Read the actual record
                record = f.read(record_length)
                if not record:
                    break

                obs_sequence.check_trailing_record_length(f, record_length) 

                if _ == 5+obs_types_definitions:
                    continue

                # Read the whole record as a string
                string_value = record.decode('utf-8').strip()
                header.append(string_value)

            # first and last obs
            # Read the record length 
            record_length = obs_sequence.read_record_length(f)

            # Read the actual record
            record = f.read(record_length)
 
            obs_sequence.check_trailing_record_length(f, record_length) 

            # Read the whole record as a two integers
            first, last = struct.unpack('ii', record)[:8]
            header.append(f"first: {first} last: {last}")

        return header

    @staticmethod
    def collect_obs_types(header):
        """Create a dictionary for the observation types in the obs_seq header"""
        num_obs_types = int(header[2])
        types = dict([x.split() for  x in header[3:num_obs_types+3]])
        return types

    @staticmethod
    def collect_copie_names(header):
        """
        Extracts the names of the copies from the header of an obs_seq file.

        Parameters:
            header (list): A list of strings representing the lines in the header of the obs_seq file.

        Returns:
            tuple: A tuple containing two elements: 
             - copie_names (list): A list of strings representing the copy names with underscores for spaces. 
             - len(copie_names) (int): The number of copy names.
        """
        for i, line in enumerate(header):
            if "num_obs:" in line and "max_num_obs:" in line:
                first_copie = i+1
                break
        copie_names = ['_'.join(x.split()) for x in header[first_copie:-1]] # first and last is last line of header
        return copie_names, len(copie_names)

    @staticmethod
    def obs_reader(file, n):
        """Reads the ascii obs sequence file and returns a generator of the obs"""
        previous_line = ''
        with open(file, 'r') as f:     
            for line in f:
                if "OBS" in line or "OBS" in previous_line:
                    if "OBS" in line:
                        obs = []
                        obs.append(line.strip()) 
                        for i in range(n+100): # number of copies + 100.  Needs to be bigger than any metadata
                            try:
                                next_line = next(f)
                            except:
                                yield obs
                                StopIteration
                                return
                            if "OBS" in next_line:
                                previous_line = next_line
                                break
                            else:
                                obs.append(next_line.strip())
                        yield obs
                    elif "OBS" in previous_line: # previous line is because I cannot use f.tell with next
                        obs = []
                        obs.append(previous_line.strip()) 
                        obs.append(line.strip()) 
                        for i in range(n+100): # number of copies + 100.  Needs to be bigger than any metadata
                            try:
                                next_line = next(f)
                            except:
                                yield obs
                                StopIteration
                                return
                            if "OBS" in next_line:
                                previous_line = next_line
                                break
                            else:
                                obs.append(next_line.strip())
                                previous_line = next_line
                        yield obs

    @staticmethod
    def check_trailing_record_length(file, expected_length):
            """Reads and checks the trailing record length from the binary file written by Fortran.

            Parameters: 
                file (file): The file object.
                expected_length (int): The expected length of the trailing record.

               Assuming 4 bytes:
               | Record Length (4 bytes) | Data (N bytes) | Trailing Record Length (4 bytes) |
            """
            trailing_record_length_bytes = file.read(4)
            trailing_record_length = struct.unpack('i', trailing_record_length_bytes)[0]
            if expected_length != trailing_record_length:
                raise ValueError("Record length mismatch in Fortran binary file")

    @staticmethod
    def read_record_length(file):
        """Reads and unpacks the record length from the file."""
        record_length_bytes = file.read(4)
        if not record_length_bytes:
            return None  # End of file
        return struct.unpack('i', record_length_bytes)[0]


    def obs_binary_reader(self, file, n):
        """Reads the obs sequence binary file and returns a generator of the obs"""
        header_length = len(self.header)
        with open(file, 'rb') as f:
            # Skip the first len(obs_seq.header) lines
            for _ in range(header_length-1):
                # Read the record length
                record_length = obs_sequence.read_record_length(f)
                if record_length is None: # End of file
                    break

                # Skip the actual record
                f.seek(record_length, 1)

                # Skip the trailing record length
                f.seek(4, 1)

            obs_num = 0
            while True:
                obs = []
                obs_num += 1
                obs.append(f"OBS        {obs_num}")              
                for _ in range(n): # number of copies
                    # Read the record length
                    record_length = obs_sequence.read_record_length(f)
                    if record_length is None:
                        break
                    # Read the actual record (copie)
                    record = f.read(record_length)
                    obs.append(struct.unpack('d', record)[0])

                    # Read the trailing record length (should match the leading one)
                    obs_sequence.check_trailing_record_length(f, record_length)
            
                # linked list info
                record_length = obs_sequence.read_record_length(f)
                if record_length is None:
                    break

                record = f.read(record_length)
                int1, int2, int3 = struct.unpack('iii', record[:12])
                linked_list_string = f"{int1:<12} {int2:<10} {int3:<12}"
                obs.append(linked_list_string)

                obs_sequence.check_trailing_record_length(f, record_length)

                # location (note no location header "loc3d" or "loc1d" for binary files)
                obs.append('loc3d')
                record_length = obs_sequence.read_record_length(f)
                record = f.read(record_length)
                x,y,z,vert = struct.unpack('dddi', record[:28])
                location_string = f"{x} {y} {z} {vert}" 
                obs.append(location_string)            

                obs_sequence.check_trailing_record_length(f, record_length)
                
                #   kind (type of observation) value
                obs.append('kind')
                record_length_bytes = f.read(4)
                record_length = struct.unpack('i', record_length_bytes)[0]
                record = f.read(record_length)
                kind = f"{struct.unpack('i', record)[0]}"
                obs.append(kind)
 
                obs_sequence.check_trailing_record_length(f, record_length)

                # time (seconds, days)
                record_length = obs_sequence.read_record_length(f)
                record = f.read(record_length)
                seconds, days = struct.unpack('ii', record)[:8]
                time_string = f"{seconds} {days}"
                obs.append(time_string)

                obs_sequence.check_trailing_record_length(f, record_length)
                
                # obs error variance
                record_length = obs_sequence.read_record_length(f)
                record = f.read(record_length)
                obs.append(struct.unpack('d', record)[0])
 
                obs_sequence.check_trailing_record_length(f, record_length)

                yield obs

    def composite_types(self, composite_types='use_default'):
        """
        Set up and construct composite types for the DataFrame.

        This function sets up composite types based on a provided YAML configuration or 
        a default configuration. It constructs new composite rows by combining specified 
        components and adds them to the DataFrame.

        Parameters:
            composite_types (str, optional): The YAML configuration for composite types. If 'use_default', the default configuration is used. Otherwise, a custom YAML configuration can be provided.

        Returns:
            pd.DataFrame: The updated DataFrame with the new composite rows added.

        Raises:
            Exception: If there are repeat values in the components.
        """

        if composite_types == 'use_default':
            composite_yaml = self.default_composite_types
        else:
            composite_yaml = composite_types
        self.composite_types_dict  = load_yaml_to_dict(composite_yaml)
        
        components = []
        for value in self.composite_types_dict.values():
            components.extend(value["components"])

        if len(components) != len(set(components)):
            raise Exception("There are repeat values in components.")

        df_comp = self.df[self.df['type'].str.upper().isin([component.upper() for component in components])]
        df_no_comp = self.df[~self.df['type'].str.upper().isin([component.upper() for component in components])]

        for key in self.composite_types_dict:
            df_new = construct_composit(df_comp, key, self.composite_types_dict[key]['components'])
            df_no_comp = pd.concat([df_no_comp, df_new], axis=0)

        return df_no_comp
        
def load_yaml_to_dict(file_path):
    """
    Load a YAML file and convert it to a dictionary.

    Parameters:
        file_path (str): The path to the YAML file.

    Returns:
        dict: The YAML file content as a dictionary.
    """
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading YAML file: {e}")
        return None        


def convert_dart_time(seconds, days):
    """covert from seconds, days after 1601 to datetime object

    Note:
        - base year for Gregorian calendar is 1601
        - dart time is seconds, days since 1601
    """
    time = dt.datetime(1601,1,1) + dt.timedelta(days=days, seconds=seconds)
    return time

def construct_composit(df_comp, composite, components):
    """
    Construct a composite DataFrame by combining rows from two components.

    This function takes two DataFrames and combines rows from them based on matching
    location and time. It creates a new row with a composite type by combining 
    specified columns using the square root of the sum of squares method.

    Parameters:
        df_comp (pd.DataFrame): The DataFrame containing the component rows to be combined.
        composite (str): The type name for the new composite rows.
        components (list of str): A list containing the type names of the two components to be combined.

    Returns:
        merged_df (pd.DataFrame): The updated DataFrame with the new composite rows added.
    """
    selected_rows = df_comp[df_comp['type'] == components[0].upper()]
    selected_rows_v = df_comp[df_comp['type'] == components[1].upper()]

    columns_to_combine = df_comp.filter(regex='ensemble').columns.tolist()
    columns_to_combine.append('observation')  # TODO HK: bias, sq_err, obs_err_var
    merge_columns = ['latitude', 'longitude', 'vertical', 'time']

    print("duplicates in u: ", selected_rows[merge_columns].duplicated().sum())
    print("duplicates in v: ",selected_rows_v[merge_columns].duplicated().sum())

    # Merge the two DataFrames on location and time columns
    merged_df = pd.merge(selected_rows, selected_rows_v, on=merge_columns, suffixes=('', '_v'))

    # Apply the square root of the sum of squares method to the relevant columns
    for col in columns_to_combine:
        merged_df[col] = np.sqrt(merged_df[col]**2 + merged_df[f'{col}_v']**2)

    # Create the new composite rows
    merged_df['type'] = composite.upper()
    merged_df = merged_df.drop(columns=[col for col in merged_df.columns if col.endswith('_v')])

    return merged_df


