---
title: 'pyDARTdiags: A Python package for manipulating observation sequences and calculating observation-space diagnostics for the Data Assimilation Research Testbed (DART)'
tags:
  - Python
  - data assimilation
  - diagnostics
  - atmospheric science

authors:
  - name: Helen Kershaw
    orcid: 0009-0002-3755-9978
    affiliation: 1
    corresponding: true
  - name: Marlee Smith
    orcid: 0009-0008-7616-9060
    affiliation: 1
  - name: Isaac Arseneau
    orcid: 0000-0003-4170-7734
    affiliation: 2
  - name: Lukas Kugler
    orcid: 0000-0002-4537-3164
    affiliation: 3 

affiliations:
  - name: NSF National Center for Atmospheric Research, Boulder CO, United States
    index: 1
    ror: 05cvfcr44
  - name: Texas Tech University
    index: 2
    ror: 0405mnx93
  - name: University of Vienna
    index: 3
    ror: 03prydq77

date: 14 July 2025
---

# Summary

pyDARTdiags is a Python package for manipulating observation sequences and calculating 
observation-space diagnostics for the Data Assimilation Research Testbed (DART). 

Data assimilation is a scientific technique that combines observations (such as measurements from
weather satellites, buoys, radar, or other sensors) with predictions from numerical models to produce
an improved estimate of the state of a system. It is widely used in fields like meteorology, 
oceanography, hydrology, and environmental science.

In Data Assimilation, observation space diagnostics are statistical analyses and visualizations
performed on the differences between model predictions and real-world observations, evaluated in
the space of the observations themselves (rather than in the model’s state space).

The Data Assimilation Research Testbed (DART) [@DARTcode],[@DART2009] is a widely used community software
facility for ensemble data assimilation. DART’s observation sequence files are central to its workflow, 
but their format and complexity can make them challenging to manipulate and analyze outside of the DART 
ecosystem. 

pyDARTdiags is a Python package created to address this challenge. It provides tools to read, manipulate,
and analyze DART observation sequence files using familiar, modern Python libraries. With pyDARTdiags,
users can extract data, compute diagnostics, and create visualizations, all within reproducible Python 
workflows that integrate seamlessly with the broader scientific ecosystem.

# Statement of need

While DART provides robust tools for data assimilation, its observation sequence files are not easily
accessible for users wishing to perform custom diagnostics or integrate with Python-based workflows.
Existing DART tools for calculation of observation-space diagnostics are written in Fortran with 
visualization in MATLAB, which may not be freely accessible to all users. pyDARTdiags provides a single 
package to process and visualize observation space diagnostics. 

PyDARTdiags ingests observation sequences into an ObsSequence object which contains the metadata about
an observation sequence, and a DataFrame containing all the data for the observations. 

This provides several advantages over the exiting Fortran+MATLAB DART software: 

- Providing Python routines for reading and writing DART observation sequence files allows the manipulation
  of observation sequences interactively via DataFrames using standard data science libraries. 
- Enabling calculation of observation-space statistics (e.g., RMSE, bias, total spread) on a DataFrame enables
  Data Assimilation researchers and users to write custom diagnostics based on DataFrames. The divide 
  between observation sequence file format and DataFrame allows updates and improvements to the DART observation
  sequence file format without breaking user created diagnostic routines. 
- Supports both static and interactive plotting (via Matplotlib and Plotly).
- Facilitates reproducible, scriptable workflows for observation-space diagnostics. A concrete use case is its 
  integration into the the CESM Regional Ocean and Carbon Configurator with Data Assimilation and Embedding 
  (CROCODILE) project, which is a community platform for accelerating observationally-constrained regional ocean
  modeling. pyDARTdiags is used for observation space diagnostics and model to observation comparison in the 
  Jupyter notebook workflows for this project.

Examples for manipulating observation sequences, visualizing observational data, and generating diagnostic plots can be 
found in the [pyDARTdiags examples gallery](https://ncar.github.io/pyDARTdiags/examples/index.html).
A detailed description of the available diagnostic statistics and available plotting functions is provided in the
[user guide](https://ncar.github.io/pyDARTdiags/userguide/index.html).
The pyDARTdiags source code is available at [https://github.com/NCAR/pyDARTdiags](https://github.com/NCAR/pyDARTdiags).


# Acknowledgements

We thank the DART team, Enrico Milanese (Woods Hole Oceanographic Institution), and the broader data 
assimilation community for their feedback and contributions.

This material is based upon work supported by the U.S. National Science Foundation under Grant No. 2311382, 
"Collaborative Research: Frameworks: A community platform for accelerating observationally-constrained 
regional oceanographic modeling", and by the NSF National Center for Atmospheric Research, which is 
a major facility sponsored by the U.S. National Science Foundation under Cooperative Agreement No. 1852977.

# References

<!-- References will be automatically included from paper.bib -->