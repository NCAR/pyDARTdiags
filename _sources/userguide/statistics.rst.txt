
.. _statistics:

===========
Statistics
===========

Observation space diagnostics is a set of metrics used to
assess the quality of data assimilation system in observation-space. 
In order to produce diagnostics in observation space, forward operators (also 
known as forward models) are used to map the model state to the observation.
A forward operator is calculated from each of the model states to give an ensemble
of 'predicted' observations. The ensemble of predicted observations together with 
the observation error is used to calculate the statistics for observation space
diagnostics.

Observation space diagnostics are calculated per observation type. 
The statistics are calculated for each observation, then averaged over all 
observations of that type in the region and time period of interest.
The region of interest may be a vertical layer, a horizontal region, or a 
combination of both.

The statistics are calculated for a DataFrame of observations using the
:mod:`stats` module. The squared error, total variance, and bias are calculated 
for each observation (row) in the DataFrame by the :func:`stats.diag_stats` function. 
`RMSE`_, `spread`_, `total spread`_, `bias`_ can calculated by aggregating over any 
number of rows to produce diagnostics for the region and time period of interest.
If the observation sequence contains posterior information, posterior statistics
will be calculated, otherwise only prior statistics will be calculated.

Definitions
-----------

Some symbols used throughout:

- :math:`y`: observation
- :math:`\epsilon`: observation error estimate
- :math:`N`: Number of observations in the group, i.e. in the region and time period of interest
- :math:`n`: group member
- :math:`\mu`: ensemble mean
- :math:`\sigma`: ensemble spread (standard deviation)
- :math:`\sigma^2`: ensemble variance

RMSE
~~~~

The root mean square error is defined

.. math::

   \text{RMSE} \equiv \sqrt{\frac{1}{N} \sum_{n=1}^{N} (\mu_n - y_n)^2}


Spread
~~~~~~

The spread is the variability among ensemble members for a given observation.

.. math::
   \sigma \equiv \sqrt{\frac{1}{N} \sum_{n=1}^{N} ( \sigma_n)^2}

Total spread
~~~~~~~~~~~~

Total Spread (:math:`\sigma_T`) is a measure of the combined uncertainty in an 
ensemble of estimated observations. It accounts for both:

- Ensemble spread (:math:`\sigma_n`):  the variability among ensemble members for
  a given observation.
- Observation error estimate (:math:`\epsilon_n`):  the expected measurement error 
  associated with each observation.

.. math::
   \sigma_T \equiv \sqrt{\frac{1}{N} \sum_{n=1}^{N} ( \sigma_n^2 + \epsilon_n^2)}

Bias
~~~~

Bias is the average difference between the ensemble mean and the observations

.. math::
   \text{bias} \equiv \frac{1}{N} \sum_{n=1}^{N} ( \mu_n - y_n)


.. _stats-multi-comp:

Multi-component Observations
-----------------------------

Some observations are multi-component, such as wind. These observations are combined from 
two (or more) scalar observations. For example, a horizontal wind observation :math:`s` is made up 
of two components, :math:`u` velocity and :math:`v` velocity.

The velocity components :math:`u` and :math:`v` are handled individually, as above, and in
addition the statistics are calculated for the magnitude of the wind vector, :math:`s`
are calculated as follows: 

.. math::
   s_y^n \equiv \sqrt{y_u^2 + y_v^2}

.. math::
   s_e^n \equiv \sqrt{\mu_u^2 + \mu_v^2}

.. math::
   \text{bias} \equiv \frac{1}{N} \sum_{n=1}^{N} (s_e^n - s_y^n)

.. math::
   \sigma_s \equiv \sqrt{\frac{1}{N} \sum_{n=1}^{N} (\sigma^2_u + \sigma^2_v )}

.. math::
   \sigma_{T,s} \equiv \sqrt{\frac{1}{N} \sum_{n=1}^{N} (\sigma^2_u + \sigma^2_v + \epsilon^2_u + \epsilon^2_v )}


.. _stats-rank-hist:

Rank Histogram
--------------

The rank histogram requires the full ensemble of forward operator values for each observation.
Sampling noise is added to each member of the forward operator ensemble.:

.. math::

   X_i = f_i + N(\mu, \sigma)

where:

- :math:`i` is the ensemble member index
- :math:`f_i` is the forward operator value of the :math:`i`-th ensemble member
- :math:`N(\mu, \sigma)` is a random number drawn from a normal distribution with the mean :math:`\mu` 
  and standard deviation :math:`\sigma`
  of the ensemble.  

The rank of the observation is the number of ensemble members :math:`X` whose value is less than the observation value.

.. math::

   R = \sum_{i=1}^{M} \mathbf{1} \left( X_i < y \right) + 1

where:

- :math:`R` is the rank of the observation :math:`X_o`,  
- :math:`M` is the number of ensemble members,  
- :math:`X_i` represents the value of the :math:`i`-th ensemble member,  
- :math:`y` is the observation value,
- :math:`\mathbf{1}(\cdot)` is the indicator function, which is 1 if :math:`X_i < y` and 0 otherwise,  
  The :math:`+1` ensures a 1-based rank (i.e., the observation is ranked among the ensemble members).  


The number of bins is equal to the number of ensemble members. 
The count :math:`H` of observations in in each  bin is: 

.. math::

   H(k) = \sum_{i=1}^{N} \mathbf{1} \left( R_i = k \right)

where:

- :math:`H(k)` is the count of forecasts that fall into rank bin :math:`k`,
- :math:`N` is the total number of observations,
- :math:`R_i` is the rank of the observation within the ensemble for case `i`,
- :math:`\mathbf{1}(\cdot)` is the indicator function, which is 1 if the condition is true and 0 otherwise.

Trusted Observations
--------------------

The DART quality control (DART_QC) values indicate, for each observation, whether the observation
was used in the assimilation, and if not, why. DART_QC 0 or 2 indicates that the observation was assimilated.
You may choose to include trusted observations in your observation space diagnostics, in which case,
include DART_QC 7 observations in the calculation of the statistics.

For reference, here is the DART QC values and their meaning. 

.. list-table:: DART Quality Control (DART_QC) Values
   :header-rows: 1

   * - QC Value
     - Description
   * - 0
     - Observation was assimilated successfully
   * - 1
     - Observation was evaluated only so not used in the assimilation
   * - 2
     - The observation was used but one or more of the posterior forward observation operators failed
   * - 3
     - The observation was evaluated only so not used AND one or more of the posterior forward observation operators failed
   * - 4
     - One or more prior forward observation operators failed so the observation was not used
   * - 5
     - The observation was not used because it was not selected in the namelist to be assimilated or evaluated
   * - 6
     - The incoming quality control value was larger than the threshold so the observation was not used
   * - 7
     - Outlier threshold test failed (as described above)
   * - 8
     - The location conversion to the vertical localization unit failed so the observation was not used


For more detail on the DART QC values refer to the 
`DART documentation <https://docs.dart.ucar.edu/en/latest/assimilation_code/modules/assimilation/quality_control_mod.html>`_.


References
----------

The notation on this page follows `<https://doi.org/doi:10.1175/2010MWR3253.1>`__.


.. See also `<https://doi.org/doi:10.1175/MWR-D-15-0052.1>`__.


