.. _quickstart:

==========
Quickstart
==========

Welcome to PyDARTdiags! This guide will help you get started with the library,
showing you how to import the modules, read observation sequence files, and perform basic operations.
For more detailed information, refer to the :ref:`userguide`.

.. code-block :: python

    import pydartdiags.obs_sequence.obs_sequence as obsq
    from pydartdiags.stats import stats
    from pydartdiags.matplots import matplots as mp

Note this example uses a small observation sequence file included with pyDARTdiags.
You can replace `datafile` with your own obs sequence file.

.. code-block :: python

    from pydartdiags.data import get_example_data
    datafile = get_example_data("obs_seq.final.1000")


Read an obs_sequence file
-------------------------

Read an observation sequence file into a DataFrame

.. code-block :: python

    obs_seq = obsq.ObsSequence(datafile)


Examine the DataFrame
---------------------

The ObsSequence object contains a Pandas DataFrame with all the observations and their associated metadata.
You can access the DataFrame using the `df` attribute of the ObsSequence object.
You can then use Pandas methods to explore the data, such as `head()` to view the first few rows.

.. code-block :: python

    obs_seq.df.head()

.. raw :: html

    <table border="1" class="dataframe">
    <thead>
        <tr style="text-align: right;">
        <th></th>
        <th>obs_num</th>
        <th>observation</th>
        <th>prior_ensemble_mean</th>
        <th>prior_ensemble_spread</th>
        <th>prior_ensemble_member_1</th>
        <th>prior_ensemble_member_2</th>
        <th>prior_ensemble_member_3</th>
        <th>prior_ensemble_member_4</th>
        <th>prior_ensemble_member_5</th>
        <th>prior_ensemble_member_6</th>
        <th>...</th>
        <th>latitude</th>
        <th>vertical</th>
        <th>vert_unit</th>
        <th>type</th>
        <th>seconds</th>
        <th>days</th>
        <th>time</th>
        <th>obs_err_var</th>
        <th>bias</th>
        <th>sq_err</th>
        </tr>
    </thead>
    <tbody>
        <tr>
        <th>0</th>
        <td>1</td>
        <td>230.16</td>
        <td>231.310652</td>
        <td>0.405191</td>
        <td>231.304725</td>
        <td>231.562874</td>
        <td>231.333915</td>
        <td>231.297690</td>
        <td>232.081416</td>
        <td>231.051063</td>
        <td>...</td>
        <td>0.012188</td>
        <td>23950.0</td>
        <td>pressure (Pa)</td>
        <td>ACARS_TEMPERATURE</td>
        <td>75603</td>
        <td>153005</td>
        <td>2019-12-01 21:00:03</td>
        <td>1.00</td>
        <td>1.150652</td>
        <td>1.324001</td>
        </tr>
        <tr>
        <th>1</th>
        <td>2</td>
        <td>18.40</td>
        <td>15.720527</td>
        <td>0.630827</td>
        <td>14.217207</td>
        <td>15.558196</td>
        <td>15.805599</td>
        <td>16.594644</td>
        <td>14.877743</td>
        <td>16.334438</td>
        <td>...</td>
        <td>0.012188</td>
        <td>23950.0</td>
        <td>pressure (Pa)</td>
        <td>ACARS_U_WIND_COMPONENT</td>
        <td>75603</td>
        <td>153005</td>
        <td>2019-12-01 21:00:03</td>
        <td>6.25</td>
        <td>-2.679473</td>
        <td>7.179578</td>
        </tr>
        <tr>
        <th>2</th>
        <td>3</td>
        <td>1.60</td>
        <td>-4.932073</td>
        <td>0.825899</td>
        <td>-5.270562</td>
        <td>-5.955998</td>
        <td>-4.209766</td>
        <td>-5.105016</td>
        <td>-4.669405</td>
        <td>-4.365305</td>
        <td>...</td>
        <td>0.012188</td>
        <td>23950.0</td>
        <td>pressure (Pa)</td>
        <td>ACARS_V_WIND_COMPONENT</td>
        <td>75603</td>
        <td>153005</td>
        <td>2019-12-01 21:00:03</td>
        <td>6.25</td>
        <td>-6.532073</td>
        <td>42.667980</td>
        </tr>
        <tr>
        <th>3</th>
        <td>4</td>
        <td>264.16</td>
        <td>264.060532</td>
        <td>0.035584</td>
        <td>264.107192</td>
        <td>264.097270</td>
        <td>264.073212</td>
        <td>264.047718</td>
        <td>264.074140</td>
        <td>264.019895</td>
        <td>...</td>
        <td>0.010389</td>
        <td>56260.0</td>
        <td>pressure (Pa)</td>
        <td>ACARS_TEMPERATURE</td>
        <td>75603</td>
        <td>153005</td>
        <td>2019-12-01 21:00:03</td>
        <td>1.00</td>
        <td>-0.099468</td>
        <td>0.009894</td>
        </tr>
        <tr>
        <th>4</th>
        <td>5</td>
        <td>11.60</td>
        <td>10.134115</td>
        <td>0.063183</td>
        <td>10.067956</td>
        <td>10.078798</td>
        <td>10.120263</td>
        <td>10.084885</td>
        <td>10.135112</td>
        <td>10.140610</td>
        <td>...</td>
        <td>0.010389</td>
        <td>56260.0</td>
        <td>pressure (Pa)</td>
        <td>ACARS_U_WIND_COMPONENT</td>
        <td>75603</td>
        <td>153005</td>
        <td>2019-12-01 21:00:03</td>
        <td>6.25</td>
        <td>-1.465885</td>
        <td>2.148818</td>
        </tr>
    </tbody>
    </table>
    <p>5 rows × 180 columns</p>



Find the number of assimilated (used) observations vs. possible observations by type

.. code-block :: python

    obs_seq.possible_vs_used()

.. raw :: html

    <table border="1" class="dataframe">
    <thead>
        <tr style="text-align: right;">
        <th></th>
        <th>type</th>
        <th>possible</th>
        <th>used</th>
        </tr>
    </thead>
    <tbody>
        <tr>
        <th>0</th>
        <td>ACARS_TEMPERATURE</td>
        <td>314</td>
        <td>233</td>
        </tr>
        <tr>
        <th>1</th>
        <td>ACARS_U_WIND_COMPONENT</td>
        <td>313</td>
        <td>227</td>
        </tr>
        <tr>
        <th>2</th>
        <td>ACARS_V_WIND_COMPONENT</td>
        <td>313</td>
        <td>228</td>
        </tr>
        <tr>
        <th>3</th>
        <td>AIRCRAFT_TEMPERATURE</td>
        <td>20</td>
        <td>14</td>
        </tr>
        <tr>
        <th>4</th>
        <td>AIRCRAFT_U_WIND_COMPONENT</td>
        <td>20</td>
        <td>14</td>
        </tr>
        <tr>
        <th>5</th>
        <td>AIRCRAFT_V_WIND_COMPONENT</td>
        <td>20</td>
        <td>13</td>
        </tr>
    </tbody>
    </table>


Examples
--------

The pyDARTdiags source comes with a set of examples in the ``examples`` directory.
The examples are also available as notebooks in the :ref:`Examples Gallery<examples-index>`.
The examples cover, :ref:`manip-examples-index`, :ref:`vis-examples-index`, and :ref:`diag-examples-index`.