import pandas as pd
import datetime as dt
import numpy as np

class obs_sequence:
    """Create an obs_sequence object from an ascii observation
       sequence file.

       Attributes:
       
           df : pandas Dataframe containing all the observations
           all_obs : list of all observations, each observation is a list
           header : header from the ascii file
           vert : dictionary of dart vertical units
           types : dictionary of types in the observation sequence file
           copie_names : names of copies in the observation sequence file.
                         Spelled copie to avoid conflict with python built-in copy function.
                         Spaces are replaced with underscores in copie_names.
           file : the input observation sequence ascii file
       
       usage: 
         Read the observation sequence from file:
              obs_seq = obs_sequence('/home/data/obs_seq.final.ascii.small')
         Access the resulting pandas dataFrame:
              obs_seq.df   

       For 3D sphere models: latitude and longitude are in degrees in the DataFrame
       sq_err = (mean-obs)**2
       bias = (mean-obs)

       rmse = sqrt( sum((mean-obs)**2)/n )
       bias = sum((mean-obs)/n)
       spread = sum(sd)
       totalspread = sqrt(sum(sd+obs_err_var)) 

       
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

    # synonyms for observation
    synonyms_for_obs = ['NCEP BUFR observation',
                        'AIRS observation', 
                        'GTSPP observation', 
                        'SST observation',
                        'observations']
    
    def __init__(self, file):
        self.loc_mod = 'None'
        self.file = file
        self.header, self.header_n = read_header(file)
        self.types = collect_obs_types(self.header)
        self.copie_names, self.n_copies = collect_copie_names(self.header)
        self.seq = obs_reader(file, self.n_copies)
        self.all_obs = self.create_all_obs() # uses up the generator
        # at this point you know if the seq is loc3d or loc1d
        if self.loc_mod == 'None':
            raise ValueError("Neither 'loc3d' nor 'loc1d' could be found in the observation sequence.")
        self.columns = self.column_headers()
        self.df = pd.DataFrame(self.all_obs, columns = self.columns)
        if self.loc_mod == 'loc3d':
            self.df['longitude'] = np.deg2rad(self.df['longitude'])
            self.df['latitude'] = np.deg2rad(self.df['latitude'])
        # rename 'X observation' to observation
        self.synonyms_for_obs = [synonym.replace(' ', '_') for synonym in self.synonyms_for_obs]
        rename_dict = {old: 'observation' for old in self.synonyms_for_obs  if old in self.df.columns}
        self.df = self.df.rename(columns=rename_dict)
        # calculate bias and sq_err is the obs_seq is an obs_seq.final
        if 'prior_ensemble_mean'.casefold() in map(str.casefold, self.columns):
            self.df['bias'] = (self.df['prior_ensemble_mean'] - self.df['observation'])
            self.df['sq_err'] = self.df['bias']**2  # squared error

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
        data.append(self.types[type_value]) # observation type
        # any observation specific obs def info is between here and the end of the list
        time = obs[-2].split()
        data.append(int(time[0])) # seconds
        data.append(int(time[1])) # days
        data.append(convert_dart_time(int(time[0]), int(time[1]))) # datetime   # HK todo what is approprate for 1d models?
        data.append(float(obs[-1])) # obs error variance ?convert to sd?
        
        return data

    def column_headers(self):
        """define the columns for the dataframe """
        heading = []
        heading.append('obs_num')
        heading.extend(self.copie_names)
        if self.loc_mod == 'loc3d':
            heading.append('longitude')
            heading.append('latitude')
            heading.append('vertical')
            heading.append('vert_unit')
        elif self.loc_mod == 'loc1d':
            heading.append('location')
        heading.append('type')
        heading.append('seconds')
        heading.append('days')
        heading.append('time')
        heading.append('obs_err_var')
        return heading

def convert_dart_time(seconds, days):
    """covert from seconds, days after 1601 to datetime object

    base year for Gregorian calendar is 1601
    dart time is seconds, days since 1601
    """
    time = dt.datetime(1601,1,1) + dt.timedelta(days=days, seconds=seconds)
    return time


def read_header(file):
    """Read the header and number of lines in the header of an obs_seq file"""
    header = []
    with open(file, 'r') as f:
        for line in f:
            if "first:" in line and "last:" in line:
                break
            else:
                header.append(line.strip())
    return header, len(header)

def collect_obs_types(header):
    """Create a dictionary for the observation types in the obs_seq header"""
    num_obs_types = int(header[2])
    types = dict([x.split() for  x in header[3:num_obs_types+3]])
    return types

def collect_copie_names(header):
    """
    Extracts the names of the copies from the header of an obs_seq file.


    Parameters:
    header (list): A list of strings representing the lines in the header of the obs_seq file.

    Returns:
    tuple: A tuple containing two elements:
        - copie_names (list): A list of strings representing the copy names with _ for spaces.
        - len(copie_names) (int): The number of copy names.
    """
    for i, line in enumerate(header):
       if "num_obs:" in line and "max_num_obs:" in line:
           first_copie = i+1
           break
    copie_names = ['_'.join(x.split()) for x in header[first_copie:]]
    return copie_names, len(copie_names)

def obs_reader(file, n):
    """Reads the obs sequence file and returns a generator of the obs"""
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
