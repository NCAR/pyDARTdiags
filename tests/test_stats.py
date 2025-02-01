# SPDX-License-Identifier: Apache-2.0
import pandas as pd
import numpy as np
import pytest
from pydartdiags.stats import stats as stats

class TestRankCalculation:

     def test_calculate_rank(self):
        data = {
            'observation': [2.5, 3.0, 4.5],  # Actual observation values
            'obs_err_var': [0.1, 0.2, 0.3],  # Variance of the observation error
            'prior_ensemble_mean': [2.4, 3.0, 4.5], 
            'prior_ensemble_member1': [2.3, 3.1, 4.6],
            'prior_ensemble_member2': [2.4, 2.9, 4.4],
            'prior_ensemble_member3': [2.5, 3.2, 4.5],
            'type': ['A', 'B', 'A']  # Observation type
        }
        df = pd.DataFrame(data)

        # Call the function
        df_hist = stats.calculate_rank(df)

        # HK @todo need a random number test to check the rank calculation
        assert 'prior_rank' in df_hist.columns
        assert 'type' in df_hist.columns

     def test_calculate_rank_posterior(self):
         data = {
            'observation': [2.5, 3.0, 4.5],  # Actual observation values
            'obs_err_var': [0.1, 0.2, 0.3],  # Variance of the observation error
            'prior_ensemble_mean': [2.4, 3.0, 4.5],
            'prior_ensemble_member1': [2.3, 3.1, 4.6],
            'prior_ensemble_member2': [2.4, 2.9, 4.4],
            'prior_ensemble_member3': [2.5, 3.2, 4.5],
            'posterior_ensemble_mean': [2.5, 3.2, 4.6],
            'posterior_ensemble_member1': [2.4, 3.2, 4.7],
            'posterior_ensemble_member2': [2.5, 3.1, 4.6],
            'posterior_ensemble_member3': [2.6, 3.3, 4.8],
            'type': ['A', 'B', 'A']  # Observation type
         }
         df = pd.DataFrame(data)

         # Call the function
         df_hist = stats.calculate_rank(df)
         print(df_hist.columns)

         # HK @todo need a random number test to check the rank calculation
         assert 'prior_rank' in df_hist.columns
         assert 'posterior_rank' in df_hist.columns
         assert 'type' in df_hist.columns

class TestMeanRoot:
    #HK do we need this?
    def test_mean_then_sqrt(self):
        # Test with a list 
        data = [1, -4, 9.1, 16]
        result = stats.mean_then_sqrt(data)
        expected = np.sqrt(np.mean(data))
        assert result == expected, f"Expected {expected}, but got {result}"

        # Test with a numpy array 
        data = np.array([1, -4, 9.1, 16])
        result = stats.mean_then_sqrt(data)
        expected = np.sqrt(np.mean(data))
        assert result == expected, f"Expected {expected}, but got {result}"

        # Test with a pandas Series of positive numbers
        data = pd.Series([1, -4, 9.1, 16])
        result = stats.mean_then_sqrt(data)
        expected = np.sqrt(np.mean(data))
        assert result == expected, f"Expected {expected}, but got {result}"

        # Test with non-numeric values
        data = ['a', 'b', 'c']
        with pytest.raises(TypeError):
            stats.mean_then_sqrt(data)



if __name__ == '__main__':
    pytest.main()