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

    # HK @todo add test for layer_statistics


class TestSelectUsedQcs:

    def test_select_used_qcs(self):
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
        result = stats.select_used_qcs(df)

        # Check if the result DataFrame has the expected rows
        expected_data = {
            "observation": [
                20.5,
                434.5,
                -5.0,
                0.0,
                1423.5,
            ],  # Observation values
            "DART_quality_control": [
                0,
                0,
                2,
                0,
                0,
            ],  # Quality control flags
            "type": [
                "A",
                "A",
                "B",
                "B",
                "A",
            ],  # Observation type
        }
        expected_df = pd.DataFrame(expected_data)

        # Assert that the result matches the expected DataFrame
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_df)


class TestPossibleVsUsed:

    def test_possible_vs_used(self):
        data = {
            "observation": [2.5, 3.0, 4.5, 5.0, 6.0],
            "DART_quality_control": [0, 1, 0, 2, 0],  # Quality control flags
            "type": ["A", "B", "A", "A", "A"],  # Observation type
        }
        df = pd.DataFrame(data)

        # Call the function
        result = stats.possible_vs_used(df)

        # Check if the result DataFrame has the expected columns
        expected_columns = ["type", "possible", "used"]
        assert all(column in result.columns for column in expected_columns)

        # Check the values of the new columns
        expected_data = {"type": ["A", "B"], "possible": [4, 1], "used": [4, 0]}
        expected_df = pd.DataFrame(expected_data)

        # Assert that the result matches the expected DataFrame
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_df)

    def test_possible_vs_used_by_layer(self):

        data = {
            "observation": [2.5, 3.0, 4.5, 5.0, 6.0],
            "DART_quality_control": [0, 1, 0, 2, 0],  # Quality control flags
            "type": ["A", "B", "A", "B", "A"],  # Observation type
            "vertical": [99, 226, 150, 250, 278],  # Pressure level
            "vert_unit": [
                "pressure (Pa)",
                "pressure (Pa)",
                "pressure (Pa)",
                "pressure (Pa)",
                "pressure (Pa)",
            ],
        }
        df = pd.DataFrame(data)

        # Define the layers
        layers = [0, 100, 200, 300]  # midpoints are 50, 150, 250
        stats.bin_by_layer(df, layers)

        # Call the function
        result = stats.possible_vs_used_by_layer(df)

        # Check if the result DataFrame has the expected columns
        expected_columns = ["type", "possible", "used", "midpoint"]
        assert all(column in result.columns for column in expected_columns)

        # Check the values of the new columns
        expected_midpoints = pd.Categorical(
            [50.0, 150.0, 250.0, 50.0, 150.0, 250.0],
            categories=[50.0, 150.0, 250.0],
            ordered=True,
        )
        expected_data = {
            "type": ["A", "A", "A", "B", "B", "B"],
            "midpoint": expected_midpoints,
            "possible": [1, 1, 1, 0, 0, 2],
            "used": [1, 1, 1, 0, 0, 1],
        }
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(result, expected_df)

    def test_possible_vs_used_by_time(self):    
        data = {
            "time": pd.to_datetime([
                "2025-01-01 00:00:00",
                "2025-01-01 00:30:00",
                "2025-01-01 01:00:00",
                "2025-01-01 01:30:00",
                "2025-01-01 02:00:00",
            ]),
            "observation": [2.5, 3.0, 4.5, 5.0, 6.0],
            "DART_quality_control": [0, 1, 0, 2, 0],  # Quality control flags
            "type": ["A", "B", "A", "A", "A"],  # Observation type
        }
        df = pd.DataFrame(data)

        # Call the function with a 1-hour time bin
        stats.bin_by_time(df, "1h")
        result = stats.possible_vs_used_by_time(df)

        # Check if the result DataFrame has the expected columns
        expected_columns = ["time_bin_midpoint", "type", "possible", "used"]
        assert all(column in result.columns for column in expected_columns)

        # Check the values of the new columns
        expected_midpoints = [
                pd.Timestamp("2025-01-01 00:29:59"),
                pd.Timestamp("2025-01-01 00:29:59"),
                pd.Timestamp("2025-01-01 01:29:59"),
                pd.Timestamp("2025-01-01 01:29:59"),
                pd.Timestamp("2025-01-01 02:29:59"),
                pd.Timestamp("2025-01-01 02:29:59"),
            ]

        expected_type = ["A", "B", "A", "B", "A", "B"]
        expected_possible =  [1, 1, 2, 0, 1, 0]
        expected_used =  [1, 0, 2, 0, 1, 0]

        assert(expected_midpoints == result["time_bin_midpoint"].tolist())
        assert(expected_type == result["type"].tolist())
        assert(expected_possible == result["possible"].tolist())
        assert(expected_used == result["used"].tolist())
        
class TestLayers:

    def test_bin_by_layer_pressure(self):
        data = {
            "observation": [2.5, 3.0, 4.5, 5.0, 6.0],
            "DART_quality_control": [0, 1, 0, 2, 0],  # Quality control flags
            "type": ["A", "B", "A", "B", "A"],  # Observation type
            "vertical": [99, 226, 150, 250, 278],  # Pressure Pa
            "vert_unit": [
                "pressure (Pa)",
                "pressure (Pa)",
                "pressure (Pa)",
                "pressure (Pa)",
                "pressure (Pa)",
            ],
        }
        df = pd.DataFrame(data)

        # Define the layers
        layers = [0, 100, 200, 300]

        # Call the function
        stats.bin_by_layer(df, layers)

        # Check if the result DataFrame has the expected columns
        expected_columns = [
            "observation",
            "DART_quality_control",
            "type",
            "vertical",
            "vert_unit",
            "vlevels",
            "midpoint",
        ]
        assert all(column in df.columns for column in expected_columns)

        # Check the values of the new columns: vlevels and midpoint
        expected_vlevels = pd.Categorical(
            [
                pd.Interval(left=0, right=100, closed="right"),
                pd.Interval(left=200, right=300, closed="right"),
                pd.Interval(left=100, right=200, closed="right"),
                pd.Interval(left=200, right=300, closed="right"),
                pd.Interval(left=200, right=300, closed="right"),
            ],
            categories=[
                pd.Interval(left=0, right=100, closed="right"),
                pd.Interval(left=100, right=200, closed="right"),
                pd.Interval(left=200, right=300, closed="right"),
            ],
            ordered=True,
        )

        expected_midpoints = pd.Categorical(
            [50.0, 250.0, 150.0, 250.0, 250.0],
            categories=[50.0, 150.0, 250.0],
            ordered=True,
        )
        data_result = {
            "observation": [2.5, 3.0, 4.5, 5.0, 6.0],
            "DART_quality_control": [0, 1, 0, 2, 0],  # Quality control flags
            "type": ["A", "B", "A", "B", "A"],  # Observation type
            "vertical": [99, 226, 150, 250, 278],  # Pressure level
            "vert_unit": [
                "pressure (Pa)",
                "pressure (Pa)",
                "pressure (Pa)",
                "pressure (Pa)",
                "pressure (Pa)",
            ],
            "vlevels": expected_vlevels,
            "midpoint": expected_midpoints,
        }

        expected_df = pd.DataFrame(data_result)
        pd.testing.assert_frame_equal(df, expected_df)

    def test_bin_by_layer_height(self):
        data = {
            "observation": [2.5, 3.0, 4.5, 5.0, 6.0],
            "DART_quality_control": [0, 1, 0, 2, 0],  # Quality control flags
            "type": ["A", "B", "A", "B", "A"],  # Observation type
            "vertical": [99, 226, 150, 250, 278],  # Height in m
            "vert_unit": [
                "height (m)",
                "height (m)",
                "height (m)",
                "height (m)",
                "height (m)",
            ],
        }
        df = pd.DataFrame(data)

        # Define the layers
        layers = [0, 100, 200, 300]

        # Call the function
        stats.bin_by_layer(df, layers, verticalUnit="height (m)")

        # Check if the result DataFrame has the expected columns
        expected_columns = [
            "observation",
            "DART_quality_control",
            "type",
            "vertical",
            "vert_unit",
            "vlevels",
            "midpoint",
        ]
        assert all(column in df.columns for column in expected_columns)

        # Check the values of the new columns: vlelvels and midpoint
        expected_vlevels = pd.Categorical(
            [
                pd.Interval(left=0, right=100, closed="right"),
                pd.Interval(left=200, right=300, closed="right"),
                pd.Interval(left=100, right=200, closed="right"),
                pd.Interval(left=200, right=300, closed="right"),
                pd.Interval(left=200, right=300, closed="right"),
            ],
            categories=[
                pd.Interval(left=0, right=100, closed="right"),
                pd.Interval(left=100, right=200, closed="right"),
                pd.Interval(left=200, right=300, closed="right"),
            ],
            ordered=True,
        )

        expected_midpoints = pd.Categorical(
            [50.0, 250.0, 150.0, 250.0, 250.0],
            categories=[50.0, 150.0, 250.0],
            ordered=True,
        )
        data_result = {
            "observation": [2.5, 3.0, 4.5, 5.0, 6.0],
            "DART_quality_control": [0, 1, 0, 2, 0],  # Quality control flags
            "type": ["A", "B", "A", "B", "A"],  # Observation type
            "vertical": [99, 226, 150, 250, 278],  # Pressure level
            "vert_unit": [
                "height (m)",
                "height (m)",
                "height (m)",
                "height (m)",
                "height (m)",
            ],
            "vlevels": expected_vlevels,
            "midpoint": expected_midpoints,
        }

        expected_df = pd.DataFrame(data_result)
        pd.testing.assert_frame_equal(df, expected_df)


class TestTimeStats:

    def test_bin_by_time(self):
        """
        Test bin_by_time with a standard case where all times fall within bins.
        """
        # Create a sample DataFrame with a 'time' column
        data = {
            "time": pd.to_datetime(
                [
                    "2025-01-01 00:00:00",
                    "2025-01-01 00:30:00",
                    "2025-01-01 01:00:00",
                    "2025-01-01 01:30:00",
                    "2025-01-01 01:34:00",
                ]
            )
        }
        df = pd.DataFrame(data)

        # Call the function with a 1-hour time bin
        stats.bin_by_time(df, "1h")

        # Expected time bins
        expected_time_bins = pd.IntervalIndex.from_tuples(
            [
                (
                    pd.Timestamp("2024-12-31 23:59:59"),
                    pd.Timestamp("2025-01-01 00:59:59"),
                ),
                (
                    pd.Timestamp("2025-01-01 00:59:59"),
                    pd.Timestamp("2025-01-01 01:59:59"),
                ),
            ]
        )

        # Expected midpoints
        expected_midpoints = [
            pd.Timestamp("2025-01-01 00:29:59"),
            pd.Timestamp("2025-01-01 00:29:59"),
            pd.Timestamp("2025-01-01 01:29:59"),
            pd.Timestamp("2025-01-01 01:29:59"),
            pd.Timestamp("2025-01-01 01:29:59"),
        ]

        # Assert that the 'time_bin' column is correct
        assert all(
            df["time_bin"].cat.categories == expected_time_bins
        ), "Time bins are incorrect."

        # Assert that the 'time_bin_midpoint' column is correct
        assert (
            list(df["time_bin_midpoint"]) == expected_midpoints
        ), "Time bin midpoints are incorrect."

        # Assert that the DataFrame has the correct number of rows
        assert len(df) == 5, "The DataFrame should have 5 rows."

    def test_bin_by_time_edge_case(self):
        """
        Test bin_by_time with a case where one of the values is exactly on the edge of the last bin.
        """
        # Create a sample DataFrame with a 'time' column
        data = {
            "time": pd.to_datetime(
                [
                    "2025-01-01 00:00:00",
                    "2025-01-01 00:30:00",
                    "2025-01-01 01:20:00",
                    "2025-01-01 01:59:59",
                    "2025-01-01 02:00:00",  # Exactly on the edge of the last bin
                ]
            )
        }
        df = pd.DataFrame(data)

        # Call the function with a 1-hour time bin
        stats.bin_by_time(df, "1h")

        # Expected time bins
        expected_time_bins = pd.IntervalIndex.from_tuples(
            [
                (
                    pd.Timestamp("2024-12-31 23:59:59"),
                    pd.Timestamp("2025-01-01 00:59:59"),
                ),
                (
                    pd.Timestamp("2025-01-01 00:59:59"),
                    pd.Timestamp("2025-01-01 01:59:59"),
                ),
                (
                    pd.Timestamp("2025-01-01 01:59:59"),
                    pd.Timestamp("2025-01-01 02:59:59"),
                ),
            ]
        )

        # Expected midpoints
        expected_midpoints = [
            pd.Timestamp("2025-01-01 00:29:59"),
            pd.Timestamp("2025-01-01 00:29:59"),
            pd.Timestamp("2025-01-01 01:29:59"),
            pd.Timestamp("2025-01-01 01:29:59"),
            pd.Timestamp("2025-01-01 02:29:59"),  # Midpoint for the last bin
        ]

        # Assert that the 'time_bin' column is correct
        assert all(
            df["time_bin"].cat.categories == expected_time_bins
        ), "Time bins are incorrect."

        # Assert that the 'time_bin_midpoint' column is correct
        assert (
            list(df["time_bin_midpoint"]) == expected_midpoints
        ), "Time bin midpoints are incorrect."

        # Assert that the DataFrame has the correct number of rows
        assert len(df) == 5, "The DataFrame should have 5 rows."


if __name__ == "__main__":
    pytest.main()
