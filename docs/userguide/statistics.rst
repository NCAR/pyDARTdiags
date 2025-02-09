
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
- :math:`\sigma`: ensemble spread
- :math:`\sigma^2`: ensemble variance

RMSE
~~~~

The root mean square error is defined

.. math::

   \text{RMSE} = \sqrt{\frac{1}{N} \sum_{n=1}^{N} (\mu_n - y_n)^2}


Spread
~~~~~~

The spread is the standard deviation of the ensemble members

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


Multi-component Observations
-----------------------------

Some observations are multi-component, such as wind. These observations are combined from 
two (or more) scalar observations. For example, a horizontal wind observation is made up 
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

Trusted Observations
--------------------

.. list-table:: Observation Quality Control (QC) Values
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

Rank Histogram
--------------


.. The notation used here is taken from `https://doi.org/doi:10.1175/2010MWR3253.1`.
   See also `https://doi.org/doi:10.1175/MWR-D-15-0052.1`.

