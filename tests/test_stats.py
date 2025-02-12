# SPDX-License-Identifier: Apache-2.0
import pandas as pd
import numpy as np
import pytest
from pydartdiags.stats import stats as stats


class TestRankCalculation:

    def test_calculate_rank(self):
        data = {
            "observation": [2.5, 3.0, 4.5],  # Actual observation values
            "obs_err_var": [0.1, 0.2, 0.3],  # Variance of the observation error
            "prior_ensemble_mean": [2.4, 3.0, 4.5],
            "prior_ensemble_member1": [2.3, 3.1, 4.6],
            "prior_ensemble_member2": [2.4, 2.9, 4.4],
            "prior_ensemble_member3": [2.5, 3.2, 4.5],
            "type": ["A", "B", "A"],  # Observation type
        }
        df = pd.DataFrame(data)

        # Call the function
        df_hist = stats.calculate_rank(df)

        # HK @todo need a random number test to check the rank calculation
        assert "prior_rank" in df_hist.columns
        assert "type" in df_hist.columns

    def test_calculate_rank_posterior(self):
        data = {
            "observation": [2.5, 3.0, 4.5],  # Actual observation values
            "obs_err_var": [0.1, 0.2, 0.3],  # Variance of the observation error
            "prior_ensemble_mean": [2.4, 3.0, 4.5],
            "prior_ensemble_member1": [2.3, 3.1, 4.6],
            "prior_ensemble_member2": [2.4, 2.9, 4.4],
            "prior_ensemble_member3": [2.5, 3.2, 4.5],
            "posterior_ensemble_mean": [2.5, 3.2, 4.6],
            "posterior_ensemble_member1": [2.4, 3.2, 4.7],
            "posterior_ensemble_member2": [2.5, 3.1, 4.6],
            "posterior_ensemble_member3": [2.6, 3.3, 4.8],
            "type": ["A", "B", "A"],  # Observation type
        }
        df = pd.DataFrame(data)

        # Call the function
        df_hist = stats.calculate_rank(df)
        print(df_hist.columns)

        # HK @todo need a random number test to check the rank calculation
        assert "prior_rank" in df_hist.columns
        assert "posterior_rank" in df_hist.columns
        assert "type" in df_hist.columns


class TestMeanRoot:
    # HK do we need this?
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
        data = ["a", "b", "c"]
        with pytest.raises(TypeError):
            stats.mean_then_sqrt(data)


class TestDiagStats:

    def test_diag_stats_prior(self):
        data = {
            "observation": [2.5, 3.0, 4.5],
            "obs_err_var": [0.1, 0.2, 0.3],
            "prior_ensemble_mean": [2.4, 3.0, 4.5],
            "prior_ensemble_spread": [0.5, 0.6, 0.7],
            "type": ["A", "B", "A"],  # Observation type
        }
        df = pd.DataFrame(data)

        # Call the function
        stats.diag_stats(df)

        # Check if the prior columns are added
        assert "prior_sq_err" in df.columns
        assert "prior_bias" in df.columns
        assert "prior_totalvar" in df.columns
        assert not "posterior_sq_err" in df.columns
        assert not "posterior_bias" in df.columns
        assert not "posterior_totalvar" in df.columns

        # Check the values of the prior columns
        expected_sq_err = [(2.4 - 2.5) ** 2, (3.0 - 3.0) ** 2, (4.5 - 4.5) ** 2]
        expected_bias = [2.4 - 2.5, 3.0 - 3.0, 4.5 - 4.5]
        expected_totalvar = [0.1 + 0.5**2, 0.2 + 0.6**2, 0.3 + 0.7**2]

        assert np.allclose(df["prior_sq_err"], expected_sq_err)
        assert np.allclose(df["prior_bias"], expected_bias)
        assert np.allclose(df["prior_totalvar"], expected_totalvar)

    def test_diag_stats_posterior(self):
        data = {
            "observation": [2.5, 3.0, 4.5],
            "obs_err_var": [0.1, 0.2, 0.3],
            "prior_ensemble_mean": [2.4, 3.0, 4.5],
            "prior_ensemble_spread": [0.5, 0.6, 0.7],
            "posterior_ensemble_mean": [2.5, 3.2, 4.6],
            "posterior_ensemble_spread": [0.4, 0.5, 0.6],
            "type": ["A", "B", "A"],  # Observation type
        }
        df = pd.DataFrame(data)

        # Call the function
        stats.diag_stats(df)

        # Check if the prior and posterior columns are added
        assert "prior_sq_err" in df.columns
        assert "prior_bias" in df.columns
        assert "prior_totalvar" in df.columns
        assert "posterior_sq_err" in df.columns
        assert "posterior_bias" in df.columns
        assert "posterior_totalvar" in df.columns

        # Check the values of the prior columns
        expected_sq_err = [(2.4 - 2.5) ** 2, (3.0 - 3.0) ** 2, (4.5 - 4.5) ** 2]
        expected_bias = [2.4 - 2.5, 3.0 - 3.0, 4.5 - 4.5]
        expected_totalvar = [0.1 + 0.5**2, 0.2 + 0.6**2, 0.3 + 0.7**2]

        assert np.allclose(df["prior_sq_err"], expected_sq_err)
        assert np.allclose(df["prior_bias"], expected_bias)
        assert np.allclose(df["prior_totalvar"], expected_totalvar)

        # Check the values of the posterior columns
        expected_sq_err = [(2.5 - 2.5) ** 2, (3.2 - 3.0) ** 2, (4.6 - 4.5) ** 2]
        expected_bias = [2.5 - 2.5, 3.2 - 3.0, 4.6 - 4.5]
        expected_totalvar = [
            0.1 + 0.4**2,
            0.2 + 0.5**2,
            0.3 + 0.6**2,
        ]  # obs error var + spread^2

        assert np.allclose(df["posterior_sq_err"], expected_sq_err)
        assert np.allclose(df["posterior_bias"], expected_bias)
        assert np.allclose(df["posterior_totalvar"], expected_totalvar)


class TestGrandStatistics:

    def test_grand_statistics_prior(self):
        data = {
            "observation": [2.5, 3.1, 4.5],
            "obs_err_var": [0.1, 0.2, 0.3],
            "prior_ensemble_mean": [2.4, 3.0, 4.5],
            "prior_ensemble_spread": [0.5, 0.6, 0.7],
            "type": ["A", "B", "A"],  # Observation type
        }
        df = pd.DataFrame(data)

        # Call diag_stats to calculate statistics
        stats.diag_stats(df)

        # Call the function
        result = stats.grand_statistics(df)

        # Check if the result DataFrame has the expected columns
        expected_columns = ["type", "prior_rmse", "prior_bias", "prior_totalspread"]
        assert all(column in result.columns for column in expected_columns)

        # Check the values of type A
        expected_rmse = np.sqrt(np.mean([(2.4 - 2.5) ** 2, (4.5 - 4.5) ** 2]))
        expected_bias = np.mean([2.4 - 2.5, 4.5 - 4.5])
        expected_totalspread = np.sqrt(np.mean([0.1 + 0.5**2, 0.3 + 0.7**2]))

        assert np.isclose(
            result.loc[result["type"] == "A", "prior_rmse"].values[0], expected_rmse
        )
        assert np.isclose(
            result.loc[result["type"] == "A", "prior_bias"].values[0], expected_bias
        )
        assert np.isclose(
            result.loc[result["type"] == "A", "prior_totalspread"].values[0],
            expected_totalspread,
        )

        # Check the values of type B
        expected_rmse = np.sqrt(np.mean([(3.0 - 3.1) ** 2]))
        expected_bias = np.mean([3.0 - 3.1])
        expected_totalspread = np.sqrt(np.mean([0.2 + 0.6**2]))

        assert np.isclose(
            result.loc[result["type"] == "B", "prior_rmse"].values[0], expected_rmse
        )
        assert np.isclose(
            result.loc[result["type"] == "B", "prior_bias"].values[0], expected_bias
        )
        assert np.isclose(
            result.loc[result["type"] == "B", "prior_totalspread"].values[0],
            expected_totalspread,
        )

    def test_grand_statistics_posterior(self):
        data = {
            "observation": [2.5, 3.02, 4.52],
            "obs_err_var": [0.1, 0.2, 0.3],
            "prior_ensemble_mean": [2.4, 3.0, 4.5],
            "prior_ensemble_spread": [0.5, 0.6, 0.7],
            "posterior_ensemble_mean": [2.51, 3.2, 4.6],
            "posterior_ensemble_spread": [0.4, 0.5, 0.6],
            "type": ["A", "B", "A"],  # Observation type
        }
        df = pd.DataFrame(data)

        # Call diag_stats to calculate statistics
        stats.diag_stats(df)

        # Call the function
        result = stats.grand_statistics(df)

        # Check if the result DataFrame has the expected columns
        expected_columns = [
            "type",
            "prior_rmse",
            "prior_bias",
            "prior_totalspread",
            "posterior_rmse",
            "posterior_bias",
            "posterior_totalspread",
        ]
        assert all(column in result.columns for column in expected_columns)

        # ------
        # Check the values of type A
        # Prior
        expected_rmse = np.sqrt(np.mean([(2.4 - 2.5) ** 2, (4.5 - 4.52) ** 2]))
        expected_bias = np.mean([2.4 - 2.5, 4.5 - 4.52])  # mean minus observation
        expected_totalspread = np.sqrt(np.mean([0.1 + 0.5**2, 0.3 + 0.7**2]))

        assert np.isclose(
            result.loc[result["type"] == "A", "prior_rmse"].values[0], expected_rmse
        )
        assert np.isclose(
            result.loc[result["type"] == "A", "prior_bias"].values[0], expected_bias
        )
        assert np.isclose(
            result.loc[result["type"] == "A", "prior_totalspread"].values[0],
            expected_totalspread,
        )

        # Posterior
        expected_rmse = np.sqrt(np.mean([(2.51 - 2.5) ** 2, (4.6 - 4.52) ** 2]))
        expected_bias = np.mean([2.51 - 2.5, 4.6 - 4.52])
        expected_totalspread = np.sqrt(np.mean([0.1 + 0.4**2, 0.3 + 0.6**2]))

        assert np.isclose(
            result.loc[result["type"] == "A", "posterior_rmse"].values[0], expected_rmse
        )
        assert np.isclose(
            result.loc[result["type"] == "A", "posterior_bias"].values[0], expected_bias
        )
        assert np.isclose(
            result.loc[result["type"] == "A", "posterior_totalspread"].values[0],
            expected_totalspread,
        )
        # ------

        # ------
        # Check the values of type B
        # Prior
        expected_rmse = np.sqrt(np.mean([(3.0 - 3.02) ** 2]))
        expected_bias = np.mean([3.0 - 3.02])
        expected_totalspread = np.sqrt(np.mean([0.2 + 0.6**2]))

        assert np.isclose(
            result.loc[result["type"] == "B", "prior_rmse"].values[0], expected_rmse
        )
        assert np.isclose(
            result.loc[result["type"] == "B", "prior_bias"].values[0], expected_bias
        )
        assert np.isclose(
            result.loc[result["type"] == "B", "prior_totalspread"].values[0],
            expected_totalspread,
        )

        # Posterior
        expected_rmse = np.sqrt(np.mean([(3.2 - 3.02) ** 2]))
        expected_bias = np.mean([3.2 - 3.02])
        expected_totalspread = np.sqrt(np.mean([0.2 + 0.5**2]))

        assert np.isclose(
            result.loc[result["type"] == "B", "posterior_rmse"].values[0], expected_rmse
        )
        assert np.isclose(
            result.loc[result["type"] == "B", "posterior_bias"].values[0], expected_bias
        )
        assert np.isclose(
            result.loc[result["type"] == "B", "posterior_totalspread"].values[0],
            expected_totalspread,
        )
        # ------


class TestSelectFailedQcs:

    def test_select_failed_qcs(self):
        data = {
            "observation": [
                20.5,
                32.0,
                434.5,
                -5.0,
                5.24,
                -24.4,
                1000.34,
                1.34,
                0.02,
                0.0,
                1423.5,
                8.2,
            ],  # Observation values
            "DART_quality_control": [
                0,
                1,
                0,
                2,
                4,
                5,
                6,
                7,
                8,
                0,
                0,
                1,
            ],  # Quality control flags
            "type": [
                "A",
                "B",
                "A",
                "B",
                "A",
                "B",
                "A",
                "B",
                "A",
                "B",
                "A",
                "B",
            ],  # Observation type
        }
        df = pd.DataFrame(data)

        # Call the function
        result = stats.select_failed_qcs(df)

        # Check if the result DataFrame has the expected rows
        expected_data = {
            "observation": [32.0, -5.0, 5.24, -24.4, 1000.34, 1.34, 0.02, 8.2],
            "DART_quality_control": [1, 2, 4, 5, 6, 7, 8, 1],
            "type": ["B", "B", "A", "B", "A", "B", "A", "B"],
        }
        expected_df = pd.DataFrame(expected_data)

        # Assert that the result matches the expected DataFrame
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_df)


if __name__ == "__main__":
    pytest.main()
