import pandas as pd

class obs_sequence:
    """Class for reading ascii observation sequence files

       usage: obs_seq = obs_sequence('/Users/hkershaw/DART/Projects/Diagnostics/data/obs_seq.final.ascii.small')
    """
    def __init__(self, file):
        self.file = file
        self.header, self.header_n = read_header(file)
        self.types = collect_obs_types(self.header)
        self.copie_names, self.n_copies = collect_copie_names(self.header)
        self.seq = obs_reader(file, self.n_copies)
        self.all_obs = self.create_all_obs() # uses up the generator
        self.columns = self.column_headers()
        self.df = pd.DataFrame(self.all_obs, columns = self.columns)
        
    def create_all_obs(self):
        count = 0
        all_obs = []
        for obs in self.seq:
            data = self.obs_to_list(obs)
            all_obs.append(data)
            count = count+1    
        return all_obs

    def obs_to_list(self, obs):
        data = []
        data.append(obs[0].split()[1]) # obs_num
        data.extend(list(map(float,obs[1:self.n_copies+1]))) # all the copies
        locI = obs.index('loc3d')
        location = obs[locI+1].split()
        data.append(location[0]) # location x
        data.append(location[1]) # location y
        data.append(location[2]) # location z
        typeI = obs.index('kind') # type of observation
        type = obs[typeI + 1]
        data.append(self.types[type]) # observation type
        time = obs[typeI + 2].split()
        data.append(time[0]) # seconds
        data.append(time[1]) # days
        return data

    def column_headers(self):
        heading = []
        heading.append('obs_num')
        heading.extend(self.copie_names)
        heading.append('longitude')
        heading.append('latitude')
        heading.append('vertical')  # need to set from which_vert
        heading.append('type')
        heading.append('seconds')
        heading.append('days')
        return heading

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
    types = dict([x.split() for  x in header[3:num_obs_types]])
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
