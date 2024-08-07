import pandas as pd
import numpy as np
import pytest
from pydartdiags.plots import plots as plts

def test_calculate_rank():
    # Example DataFrame setup
    data = {
        'observation': [2.5, 3.0, 4.5],  # Actual observation values
        'obs_err_var': [0.1, 0.2, 0.3],  # Variance of the observation error
        'prior_ensemble_member1': [2.3, 3.1, 4.6],
        'prior_ensemble_member2': [2.4, 2.9, 4.4],
        'prior_ensemble_member3': [2.5, 3.2, 4.5],
        'type': ['A', 'B', 'A']  # Observation type
    }
    df = pd.DataFrame(data)

    # Call the function
    rank, ens_size, df_hist = plts.calculate_rank(df)

    # Assertions to check if the function works as expected
    assert ens_size == 3  # 3 ensemble members
    assert 'rank' in df_hist.columns
    assert 'obstype' in df_hist.columns

def test_mean_then_sqrt():
    # Test with a list 
    data = [1, -4, 9.1, 16]
    result = plts.mean_then_sqrt(data)
    expected = np.sqrt(np.mean(data))
    assert result == expected, f"Expected {expected}, but got {result}"

    # Test with a numpy array 
    data = np.array([1, -4, 9.1, 16])
    result = plts.mean_then_sqrt(data)
    expected = np.sqrt(np.mean(data))
    assert result == expected, f"Expected {expected}, but got {result}"

    # Test with a pandas Series of positive numbers
    data = pd.Series([1, -4, 9.1, 16])
    result = plts.mean_then_sqrt(data)
    expected = np.sqrt(np.mean(data))
    assert result == expected, f"Expected {expected}, but got {result}"

      # Test with non-numeric values
    data = ['a', 'b', 'c']
    with pytest.raises(TypeError):
        plts.mean_then_sqrt(data)

# If you want to run the test directly from this script
if __name__ == "__main__":
    test_calculate_rank()