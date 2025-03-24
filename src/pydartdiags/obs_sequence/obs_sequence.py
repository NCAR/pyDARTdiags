# SPDX-License-Identifier: Apache-2.0
import pandas as pd
import datetime as dt
import numpy as np
import os
import yaml
import struct


def requires_assimilation_info(func):
    def wrapper(self, *args, **kwargs):
        if self.has_assimilation_info():
            return func(self, *args, **kwargs)
        else:
            raise ValueError(
                "Assimilation information is required to call this function."
            )

    return wrapper


class obs_sequence:
    """
    Initialize an obs_sequence object from an ASCII or binary observation sequence file,
    or create an empty obs_sequence object from scratch.

    Args:
        file (str): The input observation sequence ASCII or binary file.
                If None, an empty obs_sequence object is created from scratch.

    Returns:
        An obs_sequence object

    Attributes:
        df (pandas.DataFrame): The DataFrame containing the observation sequence data.
        header (list): The header of the observation sequence.
        copie_names (list): The names of the copies in the observation sequence.
            Spelled 'copie' to avoid conflict with the Python built-in 'copy'.
            Spaces are replaced with underscores in copie_names.
        non_qc_copie_names (list): The names of the copies not including quality control,
            e.g. observation, mean, ensemble_members
        qc_copie_names (list): The names of the quality control copies, e.g. DART_QC
        n_copies(int): The total number of copies in the observation sequence.
        n_non_qc(int): The number of copies not including quality control.
        n_qc(int): The number of quality control copies.
        vert (dict): A dictionary mapping DART vertical coordinate types to their
            corresponding integer values.

            - undefined: 'VERTISUNDEF'
            - surface: 'VERTISSURFACE' (value is surface elevation in meters)
            - model level: 'VERTISLEVEL'
            - pressure: 'VERTISPRESSURE' (in Pascals)
            - height: 'VERTISHEIGHT' (in meters)
            - scale height: 'VERTISSCALEHEIGHT' (unitless)
        loc_mod (str): The location model, either 'loc3d' or 'loc1d'.
            For 3D sphere models: latitude and longitude are in degrees in the DataFrame.
        types (dict): Dictionary of types of observations the observation sequence,
            e.g. {23: 'ACARS_TEMPERATURE'},
        reverse_types (dict): Dictionary of types with keys and values reversed, e.g
            {'ACARS_TEMPERATURE': 23}
        synonyms_for_obs (list): List of synonyms for the observation column in the DataFrame.
            The default list is

            .. code-block:: python

                [ 'NCEP BUFR observation',
                'AIRS observation',
                'GTSPP observation',
                'SST observation',
                'observations',
                'WOD observation']

            You can add more synonyms by providing a list of strings when
            creating the obs_sequence object.

            .. code-block:: python

                obs_sequence(file, synonyms=['synonym1', 'synonym2']).df

        seq (generator): Generator of observations from the observation sequence file.
        all_obs (list): List of all observations, each observation is a list.
            Valid when the obs_sequence is created from a file.
            Set to None when the obs_sequence is created from scratch or multiple
            obs_sequences are joined.
    """

    vert = {
        -2: "undefined",
        -1: "surface (m)",
        1: "model level",
        2: "pressure (Pa)",
        3: "height (m)",
        4: "scale height",
    }

    reversed_vert = {value: key for key, value in vert.items()}

    def __init__(self, file, synonyms=None):
        """
        Create an obs_sequence object from an ASCII or binary observation sequence file,
        or create an empty obs_sequence object from scratch.

        Args:
            file (str): The input observation sequence ASCII or binary file.
                    If None, an empty obs_sequence object is created from scratch.
            synonyms (list, optional): List of synonyms for the observation column in the DataFrame.

        Returns:
            an obs_sequence object
            1D observations are given a datetime of days, seconds since 2000-01-01 00:00:00
            3D observations are given a datetime of days, seconds since 1601-01-01 00:00:00 (DART Gregorian calendar)

        Examples:

            .. code-block:: python

                obs_seq = obs_sequence(file='obs_seq.final')

        """

        self.loc_mod = "None"
        self.file = file
        self.synonyms_for_obs = [
            "NCEP BUFR observation",
            "AIRS observation",
            "GTSPP observation",
            "SST observation",
            "observations",
            "WOD observation",
        ]
        if synonyms:
            if isinstance(synonyms, list):
                self.synonyms_for_obs.extend(synonyms)
            else:
                self.synonyms_for_obs.append(synonyms)

        module_dir = os.path.dirname(__file__)
        self.default_composite_types = os.path.join(module_dir, "composite_types.yaml")

        if file is None:
            # Early exit - for testing purposes or creating obs_seq objects from scratch
            self.df = pd.DataFrame()
            self.types = {}
            self.reverse_types = {}
            self.copie_names = []
            self.non_qc_copie_names = []
            self.qc_copie_names = []
            self.n_copies = 0  # copies including qc
            self.n_non_qc = 0  # copies not including qc
            self.n_qc = 0  # number of qc copies
            self.seq = []
            self.all_obs = []
            return

        if self.is_binary(file):
            self.header = self.read_binary_header(file)
        else:
            self.header = self.read_header(file)

        self.types = self.collect_obs_types(self.header)
        self.reverse_types = {v: k for k, v in self.types.items()}
        self.copie_names, self.n_copies = self.collect_copie_names(self.header)
        self.n_non_qc, self.n_qc = self.num_qc_non_qc(self.header)
        self.non_qc_copie_names = self.copie_names[: self.n_non_qc]
        self.qc_copie_names = self.copie_names[self.n_non_qc :]

        if self.is_binary(file):
            self.seq = self.obs_binary_reader(file, self.n_copies)
            self.loc_mod = "loc3d"  # only loc3d supported for binary, & no way to check
        else:
            self.seq = self.obs_reader(file, self.n_copies)

        self.all_obs = self.create_all_obs()  # uses up the generator
        # at this point you know if the seq is loc3d or loc1d
        if self.loc_mod == "None":
            raise ValueError(
                "Neither 'loc3d' nor 'loc1d' could be found in the observation sequence."
            )
        self.columns = self.column_headers()
        self.df = pd.DataFrame(self.all_obs, columns=self.columns)
        if self.loc_mod == "loc3d":
            self.df["longitude"] = np.rad2deg(self.df["longitude"])
            self.df["latitude"] = np.rad2deg(self.df["latitude"])
        # rename 'X observation' to observation
        self.synonyms_for_obs = [
            synonym.replace(" ", "_") for synonym in self.synonyms_for_obs
        ]
        rename_dict = {
            old: "observation"
            for old in self.synonyms_for_obs
            if old in self.df.columns
        }
        self.df = self.df.rename(columns=rename_dict)

    def create_all_obs(self):
        """steps through the generator to create a
        list of all observations in the sequence
        """
        all_obs = []
        for obs in self.seq:
            data = self.obs_to_list(obs)
            all_obs.append(data)
        return all_obs

    def obs_to_list(self, obs):
        """put single observation into a list"""
        data = []
        data.append(obs[0].split()[1])  # obs_num
        data.extend(list(map(float, obs[1 : self.n_copies + 1])))  # all the copies
        data.append(obs[self.n_copies + 1])  # linked list info
        try:  # HK todo only have to check loc3d or loc1d for the first observation, the whole file is the same
            locI = obs.index("loc3d")
            location = obs[locI + 1].split()
            data.append(float(location[0]))  # location x
            data.append(float(location[1]))  # location y
            data.append(float(location[2]))  # location z
            data.append(obs_sequence.vert[int(location[3])])
            self.loc_mod = "loc3d"
        except ValueError:
            try:
                locI = obs.index("loc1d")
                location = obs[locI + 1]
                data.append(float(location))  # 1d location
                self.loc_mod = "loc1d"
            except ValueError:
                raise ValueError(
                    "Neither 'loc3d' nor 'loc1d' could be found in the observation sequence."
                )
        typeI = obs.index("kind")  # type of observation
        type_value = obs[typeI + 1]
        if not self.types:
            data.append("Identity")
        else:
            data.append(self.types[type_value])  # observation type

        # any observation specific obs def info is between here and the end of the list
        # can be obs_def & external forward operator
        metadata = obs[typeI + 2 : -2]
        obs_def_metadata, external_metadata = self.split_metadata(metadata)
        data.append(obs_def_metadata)
        data.append(external_metadata)

        time = obs[-2].split()
        data.append(int(time[0]))  # seconds
        data.append(int(time[1]))  # days
        if self.loc_mod == "loc3d":
            data.append(convert_dart_time(int(time[0]), int(time[1])))
        else:  # HK todo what is appropriate for 1d models?
            data.append(
                dt.datetime(2000, 1, 1)
                + dt.timedelta(seconds=int(time[0]), days=int(time[1]))
            )
        data.append(float(obs[-1]))  # obs error variance ?convert to sd?

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
            if item.startswith("external_FO"):
                return metadata[:i], metadata[i:]
        return metadata, []

    def list_to_obs(self, data):
        """convert a list of data to an observation

        Assuming the order of the list is obs_seq.copie_names

        """
        obs = []
        obs.append("OBS        " + str(data[0]))  # obs_num lots of space
        obs.extend(data[1 : self.n_copies + 1])  # all the copies
        obs.append(data[self.n_copies + 1])  # linked list info
        obs.append("obdef")  # TODO HK: extended_FO obs_def
        obs.append(self.loc_mod)
        if self.loc_mod == "loc3d":
            obs.append(
                "   ".join(map(str, data[self.n_copies + 2 : self.n_copies + 5]))
                + "   "
                + str(self.reversed_vert[data[self.n_copies + 5]])
            )  # location x, y, z, vert
            obs.append("kind")  # this is type of observation
            obs.append(self.reverse_types[data[self.n_copies + 6]])  # observation type
            # Convert metadata to a string and append !HK @todo you are not converting to string
            obs.extend(data[self.n_copies + 7])  # metadata
            obs.extend(data[self.n_copies + 8])  # external forward operator
        elif self.loc_mod == "loc1d":
            obs.append(data[self.n_copies + 2])  # 1d location
            obs.append("kind")  # this is type of observation
            obs.append(self.reverse_types[data[self.n_copies + 3]])  # observation type
            obs.extend(data[self.n_copies + 4])  # metadata
            obs.extend(data[self.n_copies + 5])  # external forward operator
        obs.append(" ".join(map(str, data[-4:-2])))  # seconds, days
        obs.append(data[-1])  # obs error variance

        return obs

    @staticmethod
    def generate_linked_list_pattern(n):
        """Create a list of strings with the linked list pattern for n observations."""
        result = []
        for i in range(n - 1):
            col1 = i if i > 0 else -1
            col2 = i + 2
            col3 = -1
            result.append(f"{col1:<12}{col2:<11}{col3}")
        result.append(f"{n-1:<12}{'-1':<11}{'-1'}")
        return result

    def write_obs_seq(self, file):
        """
        Write the observation sequence to a file.

        This function writes the observation sequence stored in the obs_seq.DataFrame to a specified file.
        It updates the header with the number of observations, converts coordinates back to radians
        if necessary, drops unnecessary columns, sorts the DataFrame by time, and generates a linked
        list pattern for reading by DART programs.

        Args:
            file (str): The path to the file where the observation sequence will be written.

        Notes:
            - Longitude and latitude are converted back to radians if the location model is 'loc3d'.
            - The 'bias' and 'sq_err' columns are dropped if they exist in the DataFrame.
            - The DataFrame is sorted by the 'time' column.
            - An 'obs_num' column is added to the DataFrame to number the observations in time order.
            - A 'linked_list' column is generated to create a linked list pattern for the observations.

        Example:
            obsq.write_obs_seq('obs_seq.new')

        """

        self.create_header_from_dataframe()

        with open(file, "w") as f:

            for line in self.header:
                f.write(str(line) + "\n")

            # TODO HK is there something better than copying the whole thing here?
            df_copy = self.df.copy()  # copy since you want to change for writing.
            # back to radians for obs_seq
            if self.loc_mod == "loc3d":
                df_copy["longitude"] = np.deg2rad(self.df["longitude"]).round(16)
                df_copy["latitude"] = np.deg2rad(self.df["latitude"]).round(16)
            if "prior_bias" in df_copy.columns:
                df_copy = df_copy.drop(
                    columns=["prior_bias", "prior_sq_err", "prior_totalvar"]
                )
            if "posterior_bias" in df_copy.columns:
                df_copy = df_copy.drop(
                    columns=["posterior_bias", "posterior_sq_err", "posterior_totalvar"]
                )
            if "midpoint" in df_copy.columns:
                df_copy = df_copy.drop(columns=["midpoint", "vlevels"])

            # linked list for reading by dart programs
            df_copy = df_copy.sort_values(
                by=["time"], kind="stable"
            )  # sort the DataFrame by time
            df_copy.reset_index(drop=True, inplace=True)
            df_copy["obs_num"] = df_copy.index + 1  # obs_num in time order
            df_copy["linked_list"] = obs_sequence.generate_linked_list_pattern(
                len(df_copy)
            )  # linked list pattern

            def write_row(row):
                ob_write = self.list_to_obs(row.tolist())
                for line in ob_write:
                    f.write(str(line) + "\n")

            df_copy.apply(write_row, axis=1)

    @staticmethod
    def update_types_dicts(df, reverse_types):
        """
        Ensure all unique observation types are in the reverse_types dictionary and create
        the types dictionary.

        Args:
            df (pd.DataFrame): The DataFrame containing the observation sequence data.
            reverse_types (dict): The dictionary mapping observation types to their corresponding integer values.

        Returns:
            dict: The updated reverse_types dictionary.
            dict: The types dictionary with keys sorted in numerical order.
        """
        # Create a dictionary of observation types from the dataframe
        unique_types = df["type"].unique()

        # Ensure all unique types are in reverse_types
        for obs_type in unique_types:
            if obs_type not in reverse_types:
                new_id = int(max(reverse_types.values(), default=0)) + 1
                reverse_types[obs_type] = str(new_id)

        not_sorted_types = {
            reverse_types[obs_type]: obs_type for obs_type in unique_types
        }
        types = {
            k: not_sorted_types[k] for k in sorted(not_sorted_types)
        }  # to get keys in numerical order

        return reverse_types, types

    def create_header_from_dataframe(self):
        """
        Create a header for the observation sequence based on the data in the DataFrame.

        It creates a dictionary of unique observation types, counts the
        number of observations, and constructs the header with necessary information.

        Example:
        self.create_header_from_dataframe()

        """

        self.reverse_types, self.types = self.update_types_dicts(
            self.df, self.reverse_types
        )

        num_obs = len(self.df)

        self.header = []
        self.header.append("obs_sequence")
        self.header.append("obs_type_definitions")
        self.header.append(f"{len(self.types)}")
        for key, value in self.types.items():
            self.header.append(f"{key} {value}")
        self.header.append(
            f"num_copies: {self.n_non_qc}  num_qc: {self.n_qc}"
        )  # @todo HK not keeping track if num_qc changes
        self.header.append(f"num_obs: {num_obs:>10} max_num_obs: {num_obs:>10}")
        stats_cols = [
            "prior_bias",
            "prior_sq_err",
            "prior_totalvar",
            "posterior_bias",
            "posterior_sq_err",
            "posterior_totalvar",
        ]
        level_cols = ["vlevels", "midpoint"]
        non_copie_cols = [
            "obs_num",
            "linked_list",
            "longitude",
            "latitude",
            "vertical",
            "vert_unit",
            "type",
            "metadata",
            "external_FO",
            "seconds",
            "days",
            "time",
            "obs_err_var",
            "location",
        ]
        for copie in self.df.columns:
            if copie not in stats_cols + non_copie_cols + level_cols:
                self.header.append(copie.replace("_", " "))
        first = 1
        self.header.append(f"first: {first:>12} last: {num_obs:>12}")

    def column_headers(self):
        """define the columns for the dataframe"""
        heading = []
        heading.append("obs_num")
        heading.extend(self.copie_names)
        heading.append("linked_list")
        if self.loc_mod == "loc3d":
            heading.append("longitude")
            heading.append("latitude")
            heading.append("vertical")
            heading.append("vert_unit")
        elif self.loc_mod == "loc1d":
            heading.append("location")
        heading.append("type")
        heading.append("metadata")
        heading.append("external_FO")
        heading.append("seconds")
        heading.append("days")
        heading.append("time")
        heading.append("obs_err_var")
        return heading

    @requires_assimilation_info
    def select_by_dart_qc(self, dart_qc):
        """
        Selects rows from a DataFrame based on the DART quality control flag.

        Args:
            df (DataFrame): A pandas DataFrame.
            dart_qc (int): The DART quality control flag to select.

        Returns:
            DataFrame: A DataFrame containing only the rows with the specified DART quality control flag.

        Raises:
            ValueError: If the DART quality control flag is not present in the DataFrame.
        """
        if dart_qc not in self.df["DART_quality_control"].unique():
            raise ValueError(
                f"DART quality control flag '{dart_qc}' not found in DataFrame."
            )
        else:
            return self.df[self.df["DART_quality_control"] == dart_qc]

    @requires_assimilation_info
    def select_used_qcs(self):
        """
        Select rows from the DataFrame where the observation was used.
        Includes observations for which the posterior forward observation operators failed.

        Returns:
            pandas.DataFrame: A DataFrame containing only the rows with a DART quality control flag 0 or 2.
        """
        return self.df[
            (self.df["DART_quality_control"] == 0)
            | (self.df["DART_quality_control"] == 2)
        ]

    @requires_assimilation_info
    def possible_vs_used(self):
        """
        Calculates the count of possible vs. used observations by type.

        This function takes a DataFrame containing observation data, including a 'type' column for the observation
        type and an 'observation' column. The number of used observations ('used'), is the total number
        of assimilated observations (as determined by the `select_used_qcs` function).
        The result is a DataFrame with each observation type, the count of possible observations, and the count of
        used observations.

        Returns:
            pd.DataFrame: A DataFrame with three columns: 'type', 'possible', and 'used'. 'type' is the observation type,
            'possible' is the count of all observations of that type, and 'used' is the count of observations of that type
            that passed quality control checks.
        """
        possible = self.df.groupby("type")["observation"].count()
        possible.rename("possible", inplace=True)

        used_qcs = self.select_used_qcs().groupby("type")["observation"].count()
        used = used_qcs.reindex(possible.index, fill_value=0)
        used.rename("used", inplace=True)

        return pd.concat([possible, used], axis=1).reset_index()

    @staticmethod
    def is_binary(file):
        """Check if a file is binary file."""
        with open(file, "rb") as f:
            chunk = f.read(1024)
            if b"\0" in chunk:
                return True
        return False

    @staticmethod
    def read_header(file):
        """Read the header and number of lines in the header of an ascii obs_seq file"""
        header = []
        with open(file, "r") as f:
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
        with open(file, "rb") as f:
            while True:
                # Read the record length
                record_length = obs_sequence.read_record_length(f)
                if record_length is None:
                    break
                record = f.read(record_length)
                if not record:  # end of file
                    break

                # Read the trailing record length (should match the leading one)
                obs_sequence.check_trailing_record_length(f, record_length)

                linecount += 1

                if linecount == 3:
                    obs_types_definitions = struct.unpack("i", record)[0]
                    continue

                if linecount == 4 + obs_types_definitions:
                    num_copies, num_qcs, num_obs, max_num_obs = struct.unpack(
                        "iiii", record
                    )[:16]
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
                header.append(record.decode("utf-8").strip())

            header.append(str(obs_types_definitions))

            # obs_types_definitions
            for _ in range(3, 4 + obs_types_definitions):
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
                    continue  # num obs_types_definitions
                # Read an integer and a string from the record
                integer_value = struct.unpack("i", record[:4])[0]
                string_value = record[4:].decode("utf-8").strip()
                header.append(f"{integer_value} {string_value}")

            header.append(f"num_copies:   {num_copies}  num_qc:   {num_qcs}")
            header.append(f"num_obs: {num_obs}  max_num_obs: {max_num_obs}")

            # copie names
            for _ in range(
                5 + obs_types_definitions,
                5 + obs_types_definitions + num_copies + num_qcs + 1,
            ):
                # Read the record length
                record_length = obs_sequence.read_record_length(f)
                if record_length is None:
                    break

                # Read the actual record
                record = f.read(record_length)
                if not record:
                    break

                obs_sequence.check_trailing_record_length(f, record_length)

                if _ == 5 + obs_types_definitions:
                    continue

                # Read the whole record as a string
                string_value = record.decode("utf-8").strip()
                header.append(string_value)

            # first and last obs
            # Read the record length
            record_length = obs_sequence.read_record_length(f)

            # Read the actual record
            record = f.read(record_length)

            obs_sequence.check_trailing_record_length(f, record_length)

            # Read the whole record as a two integers
            first, last = struct.unpack("ii", record)[:8]
            header.append(f"first: {first} last: {last}")

        return header

    @staticmethod
    def collect_obs_types(header):
        """Create a dictionary for the observation types in the obs_seq header"""
        num_obs_types = int(header[2])
        types = dict([x.split() for x in header[3 : num_obs_types + 3]])
        return types

    @staticmethod
    def collect_copie_names(header):
        """
        Extracts the names of the copies from the header of an obs_seq file.

        Args:
            header (list): A list of strings representing the lines in the header of the obs_seq file.

        Returns:
            tuple: A tuple containing two elements:
             - copie_names (list): A list of strings representing the copy names with underscores for spaces.
             - len(copie_names) (int): The number of copy names.
        """
        for i, line in enumerate(header):
            if "num_obs:" in line and "max_num_obs:" in line:
                first_copie = i + 1
                break
        copie_names = [
            "_".join(x.split()) for x in header[first_copie:-1]
        ]  # first and last is last line of header
        return copie_names, len(copie_names)

    @staticmethod
    def num_qc_non_qc(header):
        """Find the number of qc and non-qc copies in the header"""
        for line in header:
            if "num_copies:" in line and "num_qc:" in line:
                num_non_qc = int(line.split()[1])
                num_qc = int(line.split()[3])
                return num_non_qc, num_qc

    @staticmethod
    def obs_reader(file, n):
        """Reads the ascii obs sequence file and returns a generator of the obs"""
        previous_line = ""
        with open(file, "r") as f:
            for line in f:
                if "OBS" in line or "OBS" in previous_line:
                    if "OBS" in line:
                        obs = []
                        obs.append(line.strip())
                        for i in range(
                            n + 100
                        ):  # number of copies + 100.  Needs to be bigger than any metadata
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
                    elif (
                        "OBS" in previous_line
                    ):  # previous line is because I cannot use f.tell with next
                        obs = []
                        obs.append(previous_line.strip())
                        obs.append(line.strip())
                        for i in range(
                            n + 100
                        ):  # number of copies + 100.  Needs to be bigger than any metadata
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

        Args:
            file (file): The file object.
            expected_length (int): The expected length of the trailing record.

           Assuming 4 bytes:
           | Record Length (4 bytes) | Data (N bytes) | Trailing Record Length (4 bytes) |
        """
        trailing_record_length_bytes = file.read(4)
        trailing_record_length = struct.unpack("i", trailing_record_length_bytes)[0]
        if expected_length != trailing_record_length:
            raise ValueError("Record length mismatch in Fortran binary file")

    @staticmethod
    def read_record_length(file):
        """Reads and unpacks the record length from the file."""
        record_length_bytes = file.read(4)
        if not record_length_bytes:
            return None  # End of file
        return struct.unpack("i", record_length_bytes)[0]

    def obs_binary_reader(self, file, n):
        """Reads the obs sequence binary file and returns a generator of the obs"""
        header_length = len(self.header)
        with open(file, "rb") as f:
            # Skip the first len(obs_seq.header) lines
            for _ in range(header_length - 1):
                # Read the record length
                record_length = obs_sequence.read_record_length(f)
                if record_length is None:  # End of file
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
                for _ in range(n):  # number of copies
                    # Read the record length
                    record_length = obs_sequence.read_record_length(f)
                    if record_length is None:
                        break
                    # Read the actual record (copie)
                    record = f.read(record_length)
                    obs.append(struct.unpack("d", record)[0])

                    # Read the trailing record length (should match the leading one)
                    obs_sequence.check_trailing_record_length(f, record_length)

                # linked list info
                record_length = obs_sequence.read_record_length(f)
                if record_length is None:
                    break

                record = f.read(record_length)
                int1, int2, int3 = struct.unpack("iii", record[:12])
                linked_list_string = f"{int1:<12} {int2:<10} {int3:<12}"
                obs.append(linked_list_string)

                obs_sequence.check_trailing_record_length(f, record_length)

                # location (note no location header "loc3d" or "loc1d" for binary files)
                obs.append("loc3d")
                record_length = obs_sequence.read_record_length(f)
                record = f.read(record_length)
                x, y, z, vert = struct.unpack("dddi", record[:28])
                location_string = f"{x} {y} {z} {vert}"
                obs.append(location_string)

                obs_sequence.check_trailing_record_length(f, record_length)

                #   kind (type of observation) value
                obs.append("kind")
                record_length_bytes = f.read(4)
                record_length = struct.unpack("i", record_length_bytes)[0]
                record = f.read(record_length)
                kind = f"{struct.unpack('i', record)[0]}"
                obs.append(kind)

                obs_sequence.check_trailing_record_length(f, record_length)

                # time (seconds, days)
                record_length = obs_sequence.read_record_length(f)
                record = f.read(record_length)
                seconds, days = struct.unpack("ii", record)[:8]
                time_string = f"{seconds} {days}"
                obs.append(time_string)

                obs_sequence.check_trailing_record_length(f, record_length)

                # obs error variance
                record_length = obs_sequence.read_record_length(f)
                record = f.read(record_length)
                obs.append(struct.unpack("d", record)[0])

                obs_sequence.check_trailing_record_length(f, record_length)

                yield obs

    def composite_types(self, composite_types="use_default"):
        """
        Set up and construct composite types for the DataFrame.

        This function sets up composite types based on a provided YAML configuration or
        a default configuration. It constructs new composite rows by combining specified
        components and adds them to the DataFrame.

        Args:
            composite_types (str, optional): The YAML configuration for composite types.
            If 'use_default', the default configuration is used. Otherwise, a custom YAML configuration can be provided.

        Returns:
            pd.DataFrame: The updated DataFrame with the new composite rows added.

        Raises:
            Exception: If there are repeat values in the components.
        """

        if composite_types == "use_default":
            composite_yaml = self.default_composite_types
        else:
            composite_yaml = composite_types
        self.composite_types_dict = load_yaml_to_dict(composite_yaml)

        components = []
        for value in self.composite_types_dict.values():
            components.extend(value["components"])

        if len(components) != len(set(components)):
            raise Exception("There are repeat values in components.")

        # data frame for the composite types
        df_comp = self.df[
            self.df["type"]
            .str.upper()
            .isin([component.upper() for component in components])
        ]

        df = pd.DataFrame()
        for key in self.composite_types_dict:
            df_new = construct_composit(
                df_comp, key, self.composite_types_dict[key]["components"]
            )
            df = pd.concat([df, df_new], axis=0)

        # add the composite types to the DataFrame
        self.df = pd.concat([self.df, df], axis=0)
        return

    @classmethod
    def join(cls, obs_sequences, copies=None):
        """
        Join a list of observation sequences together.

        This method combines the headers and observations from a list of obs_sequence objects
        into a single obs_sequence object.

        Args:
            obs_sequences (list of obs_sequences): The list of observation sequences objects to join.
            copies (list of str, optional): A list of copy names to include in the combined data.
                    If not provided, all copies are included.

        Returns:
            A new obs_sequence object containing the combined data.

        Example:
            .. code-block:: python

                obs_seq1 = obs_sequence(file='obs_seq1.final')
                obs_seq2 = obs_sequence(file='obs_seq2.final')
                obs_seq3 = obs_sequence(file='obs_seq3.final')
                combined = obs_sequence.join([obs_seq1, obs_seq2, obs_seq3])
        """
        if not obs_sequences:
            raise ValueError("The list of observation sequences is empty.")

        # Create a new obs_sequnece object with the combined data
        combo = cls(file=None)

        # Check if all obs_sequences have compatible attributes
        first_loc_mod = obs_sequences[0].loc_mod
        first_has_assimilation_info = obs_sequences[0].has_assimilation_info()
        first_has_posterior = obs_sequences[0].has_posterior()
        for obs_seq in obs_sequences:
            if obs_seq.loc_mod != first_loc_mod:
                raise ValueError(
                    "All observation sequences must have the same loc_mod."
                )
            if obs_seq.has_assimilation_info() != first_has_assimilation_info:
                raise ValueError(
                    "All observation sequences must have assimilation info."
                )
            if obs_seq.has_posterior() != first_has_posterior:
                raise ValueError(
                    "All observation sequences must have the posterior info."
                )
                # HK @todo prior only
        combo.loc_mod = first_loc_mod

        # check the copies are compatible (list of copies to combine?)
        # subset of copies if needed   # @todo HK 1d or 3d
        if copies:
            start_required_columns = ["obs_num", "observation"]
            end_required_columns = [
                "linked_list",
                "longitude",
                "latitude",
                "vertical",
                "vert_unit",
                "type",
                "metadata",
                "external_FO",
                "seconds",
                "days",
                "time",
                "obs_err_var",
            ]
            required_columns = start_required_columns + end_required_columns

            requested_columns = (
                start_required_columns
                + [item for item in copies if item not in required_columns]
                + end_required_columns
            )

            for obs_seq in obs_sequences:
                if not set(requested_columns).issubset(obs_seq.df.columns):
                    raise ValueError(
                        "All observation sequences must have the selected copies."
                    )

            # go through columns and create header
            remove_list = [
                "obs_num",
                "linked_list",
                "latitude",
                "longitude",
                "vertical",
                "vert_unit",
                "type",
                "metadata",
                "external_FO",
                "time",
                "seconds",
                "days",
                "obs_err_var",
            ]
            # using lists to retain copy order, non_qcs followed by qcs
            combo.copie_names = [
                item for item in requested_columns if item not in remove_list
            ]
            combo.non_qc_copie_names = [
                item
                for item in combo.copie_names
                if item in obs_sequences[0].non_qc_copie_names
            ]
            combo.qc_copie_names = [
                item
                for item in combo.copie_names
                if item in obs_sequences[0].qc_copie_names
            ]

            combo.n_copies = len(combo.copie_names)
            combo.n_qc = len(combo.qc_copie_names)
            combo.n_non_qc = len(combo.non_qc_copie_names)

        else:
            for obs_seq in obs_sequences:
                if not obs_sequences[0].df.columns.isin(obs_seq.df.columns).all():
                    raise ValueError(
                        "All observation sequences must have the same copies."
                    )
            combo.n_copies = obs_sequences[0].n_copies
            combo.n_qc = obs_sequences[0].n_qc
            combo.n_non_qc = obs_sequences[0].n_non_qc
            combo.copie_names = obs_sequences[0].copie_names

        # todo HK @todo combine synonyms for obs?

        # Initialize combined data
        combined_types = []
        combined_df = pd.DataFrame()
        combo.all_obs = None  # set to none to force writing from the dataframe if write_obs_seq is called

        # Iterate over the list of observation sequences and combine their data
        for obs_seq in obs_sequences:
            if copies:
                combined_df = pd.concat(
                    [combined_df, obs_seq.df[requested_columns]], ignore_index=True
                )
            else:
                combined_df = pd.concat([combined_df, obs_seq.df], ignore_index=True)
            combined_types.extend(list(obs_seq.reverse_types.keys()))

        # create dictionary of types
        keys = set(combined_types)
        combo.reverse_types = {item: i + 1 for i, item in enumerate(keys)}
        combo.types = {v: k for k, v in combo.reverse_types.items()}

        # create linked list for obs
        combo.df = combined_df.sort_values(by="time").reset_index(drop=True)
        combo.df["linked_list"] = obs_sequence.generate_linked_list_pattern(
            len(combo.df)
        )
        combo.df["obs_num"] = combined_df.index + 1
        combo.create_header(len(combo.df))

        return combo

    def has_assimilation_info(self):
        """
        Check if the DataFrame has prior information.

        Returns:
            bool: True if both 'prior_ensemble_mean' and 'prior_ensemble_spread' columns are present, False otherwise.
        """
        return "prior_ensemble_mean".casefold() in map(
            str.casefold, self.df.columns
        ) and "prior_ensemble_spread".casefold() in map(str.casefold, self.df.columns)

    def has_posterior(self):
        """
        Check if the DataFrame has posterior information.

        Returns:
            bool: True if both 'posterior_ensemble_mean' and 'posterior_ensemble_spread' columns are present, False otherwise.
        """
        return "posterior_ensemble_mean".casefold() in map(
            str.casefold, self.df.columns
        ) and "posterior_ensemble_spread".casefold() in map(
            str.casefold, self.df.columns
        )

    def create_header(self, n):
        """Create a header for the obs_seq file from the obs_sequence object."""
        assert (
            self.n_copies == self.n_non_qc + self.n_qc
        ), "n_copies must be equal to n_non_qc + n_qc"

        self.header = []
        self.header.append(f"obs_sequence")
        self.header.append("obs_type_definitions")
        self.header.append(f"{len(self.types)}")
        for key, value in self.types.items():
            self.header.append(f"{key} {value}")
        self.header.append(f"num_copies: {self.n_non_qc}  num_qc: {self.n_qc}")
        self.header.append(f"num_obs: {n}  max_num_obs: {n}")
        for copie in self.copie_names:
            self.header.append(copie)
        self.header.append(f"first: 1 last: {n}")


def load_yaml_to_dict(file_path):
    """
    Load a YAML file and convert it to a dictionary.

    Args:
        file_path (str): The path to the YAML file.

    Returns:
        dict: The YAML file content as a dictionary.
    """
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading YAML file: {e}")
        raise


def convert_dart_time(seconds, days):
    """covert from seconds, days after 1601 to datetime object

    Note:
        - base year for Gregorian calendar is 1601
        - dart time is seconds, days since 1601
    """
    time = dt.datetime(1601, 1, 1) + dt.timedelta(days=days, seconds=seconds)
    return time


def construct_composit(df_comp, composite, components):
    """
    Construct a composite DataFrame by combining rows from two components.

    This function takes two DataFrames and combines rows from them based on matching
    location and time. It creates a new row with a composite type by combining
    specified columns using the square root of the sum of squares method.

    Args:
        df_comp (pd.DataFrame): The DataFrame containing the component rows to be combined.
        composite (str): The type name for the new composite rows.
        components (list of str): A list containing the type names of the two components to be combined.

    Returns:
        merged_df (pd.DataFrame): A DataFrame containing the new composite rows.
    """
    selected_rows = df_comp[df_comp["type"] == components[0].upper()]
    selected_rows_v = df_comp[df_comp["type"] == components[1].upper()]

    prior_columns_to_combine = df_comp.filter(regex="prior_ensemble").columns.tolist()
    posterior_columns_to_combine = df_comp.filter(
        regex="posterior_ensemble"
    ).columns.tolist()
    columns_to_combine = (
        prior_columns_to_combine
        + posterior_columns_to_combine
        + ["observation", "obs_err_var"]
    )
    merge_columns = ["latitude", "longitude", "vertical", "time"]
    same_obs_columns = merge_columns + [
        "observation",
        "obs_err_var",
    ]  # same observation is duplicated

    if (
        selected_rows[same_obs_columns].duplicated().sum() > 0
        or selected_rows_v[same_obs_columns].duplicated().sum() > 0
    ):
        print(
            f"{selected_rows[same_obs_columns].duplicated().sum()} duplicates in {composite} component {components[0]}: "
        )
        print(f"{selected_rows[same_obs_columns]}")
        print(
            f"{selected_rows_v[same_obs_columns].duplicated().sum()} duplicates in {composite} component {components[0]}: "
        )
        print(f"{selected_rows_v[same_obs_columns]}")
        raise Exception("There are duplicates in the components.")

    # Merge the two DataFrames on location and time columns
    merged_df = pd.merge(
        selected_rows, selected_rows_v, on=merge_columns, suffixes=("", "_v")
    )

    # Apply the square root of the sum of squares method to the relevant columns
    for col in columns_to_combine:
        merged_df[col] = np.sqrt(merged_df[col] ** 2 + merged_df[f"{col}_v"] ** 2)

    # Create the new composite rows
    merged_df["type"] = composite.upper()
    merged_df = merged_df.drop(
        columns=[col for col in merged_df.columns if col.endswith("_v")]
    )

    return merged_df
