# pyDARTdiag

Playground for python tools for DART Observation Space Diagnostics

* obs\_sequence to DataFrame

Example importing the obs\_sequence module from a file

```
import sys
import os
sys.path.append(os.path.abspath("/Users/hkershaw/DART/Projects/Diagnostics/pyDART/src/obs_sequence"))

import obs_sequence as dart_os

obs_seq = dart_os.obs_sequence('obs_seq.final.ascii.test_meta')

obs_seq.df
```
