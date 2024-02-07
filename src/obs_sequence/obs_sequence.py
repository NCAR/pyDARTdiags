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
           copie_names : names of copies in the observation sequence file
           file : the input observation sequence ascii file
       
       usage: 
         Read the observation sequence from file:
              obs_seq = obs_sequence('/home/data/obs_seq.final.ascii.small')
         Access the resutling pandas dataFrame:
              obs_seq.df   

       latitude and longitude are in degress in the DataFrame
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
    #   model level ''VERTISLEVEL'
    #   pressure 'VERTISPRESSURE' (in pascals)
    #   height 'VERTISHEIGHT' (in meters)
    #   scale height 'VERTISSCALEHEIGHT' (unitless)
    vert = {-2: 'undefined',              
            -1: 'surface (m)', 
             1: 'model level',
             2: 'pressue (Pa)',
             3: 'height (m)',
             4: 'scale height' }
    
    def __init__(self, file):
        self.file = file
        self.header, self.header_n = read_header(file)
        self.types = collect_obs_types(self.header)
        self.copie_names, self.n_copies = collect_copie_names(self.header)
        self.seq = obs_reader(file, self.n_copies)
        self.all_obs = self.create_all_obs() # uses up the generator
        self.columns = self.column_headers()
        self.df = pd.DataFrame(self.all_obs, columns = self.columns)
        self.df['longitude'] = np.rad2deg(self.df['longitude'])
        self.df['latitude'] = np.rad2deg(self.df['latitude'])
        self.df['bias'] = (self.df['prior_ensemble_mean'] - self.df['observation'])
        self.df['sq_err'] = self.df['bias']**2  # squared error

    def create_all_obs(self):
        """ steps thougth the generator to create a
            list of all observations in the sequence 
        """
        count = 0
        all_obs = []
        for obs in self.seq:
            data = self.obs_to_list(obs)
            all_obs.append(data)
            count = count+1    
        return all_obs

    def obs_to_list(self, obs):
        """put single observation into a list
           discards obs_def
        """
        data = []
        data.append(obs[0].split()[1]) # obs_num
        data.extend(list(map(float,obs[1:self.n_copies+1]))) # all the copies
        locI = obs.index('loc3d')
        location = obs[locI+1].split()
        data.append(float(location[0])) # location x
        data.append(float(location[1])) # location y
        data.append(float(location[2])) # location z
        data.append(obs_sequence.vert[int(location[3])])
        typeI = obs.index('kind') # type of observation
        type_value = obs[typeI + 1]
        data.append(self.types[type_value]) # observation type
        # any observation specific obs def info is between here and the end of the list
        time = obs[-2].split()
        data.append(int(time[0])) # seconds
        data.append(int(time[1])) # days
        data.append(convert_dart_time(int(time[0]), int(time[1]))) # datetime
        data.append(obs[-1]) # obs error variance ?convert to sd?
        
        return data

    def column_headers(self):
        """define the columns for the dataframe """
        heading = []
        heading.append('obs_num')
        heading.extend(self.copie_names)
        heading.append('longitude')
        heading.append('latitude')
        heading.append('vertical')
        heading.append('vert_unit')
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
   """Create list of copy names. Spelled copie"""
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
