.. _obs_sequence:

====================
module: obs_sequence
====================

.. autoclass:: obs_sequence.ObsSequence


=================================
Attributes of ObsSequence Objects
=================================

df
    *(pandas.DataFrame)*  
    The DataFrame containing the observation sequence data.

header
    *(list)*  
    The header of the observation sequence.

copie_names
    *(list)*  
    The names of the copies in the observation sequence.  
    Spelled 'copie' to avoid conflict with the Python built-in 'copy'.  
    Spaces are replaced with underscores in copie_names.

non_qc_copie_names
    *(list)*  
    The names of the copies not including quality control, e.g. observation, mean, ensemble_members

qc_copie_names
    *(list)*  
    The names of the quality control copies, e.g. DART_QC

n_copies
    *(int)*  
    The total number of copies in the observation sequence.

n_non_qc
    *(int)*  
    The number of copies not including quality control.

n_qc
    *(int)*  
    The number of quality control copies.

vert
    *(dict)*  
    A dictionary mapping DART vertical coordinate types to their corresponding integer values:
    
    - undefined: 'VERTISUNDEF'
    - surface: 'VERTISSURFACE' (value is surface elevation in meters)
    - model level: 'VERTISLEVEL'
    - pressure: 'VERTISPRESSURE' (in Pascals)
    - height: 'VERTISHEIGHT' (in meters)
    - scale height: 'VERTISSCALEHEIGHT' (unitless)

loc_mod
    *(str)*  
    The location model, either 'loc3d' or 'loc1d'.  
    For 3D sphere models: latitude and longitude are in degrees in the DataFrame.

types
    *(dict)*  
    Dictionary of types of observations in the observation sequence, e.g. {23: 'ACARS_TEMPERATURE'}

reverse_types
    *(dict)*  
    Dictionary of types with keys and values reversed, e.g. {'ACARS_TEMPERATURE': 23}

synonyms_for_obs
    *(list)*  
    List of synonyms for the observation column in the DataFrame.

all_obs
    *(list)*  
    List of all observations, each observation is a list.  
    Valid when the ObsSequence is created from a file.  
    Set to None when the ObsSequence is created from scratch or multiple ObsSequences are joined.

=======================
ObsSequence Methods
=======================

.. automethod:: obs_sequence.ObsSequence.write_obs_seq 
.. automethod:: obs_sequence.ObsSequence.possible_vs_used
.. automethod:: obs_sequence.ObsSequence.select_by_dart_qc
.. automethod:: obs_sequence.ObsSequence.select_used_qcs
.. automethod:: obs_sequence.ObsSequence.composite_types  
.. automethod:: obs_sequence.ObsSequence.join

.. automethod:: obs_sequence.ObsSequence.update_attributes_from_df
.. automethod:: obs_sequence.ObsSequence.create_header_from_dataframe 
.. automethod:: obs_sequence.ObsSequence.create_header

.. automethod:: obs_sequence.ObsSequence.has_posterior
.. automethod:: obs_sequence.ObsSequence.has_assimilation_info


