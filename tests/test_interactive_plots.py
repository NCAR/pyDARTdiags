# SPDX-License-Identifier: Apache-2.0
import pytest
import json
import pandas as pd
from pydartdiags.obs_sequence import obs_sequence as obsq
from pydartdiags.interactive_plots import interactive_plots as ip


class TestGeoPlot:
    @pytest.fixture
    def obs_seq(self):
        # Sample dataframe for testing
        data = {
            "latitude": [10.0, 20.0, 30.0],
            "longitude": [40.0, 50.0, 60.0],
            "type": ["ACARS_TEMPERATURE", "RADIOSONDE_U_WIND_COMPONENT", "ACARS_TEMPERATURE"],
            "observation": [1.0, 2.0, 3.0],
            "obs_num": [1001, 1002, 1003],
            "DART_quality_control": [0, 1, 2],
        }
        df = pd.DataFrame(data)

        # Create an instance of obs_sequence with the sample DataFrame
        obs_seq = obsq.ObsSequence(file=None)
        obs_seq.df = df
        return obs_seq

    @pytest.fixture
    def obs_seq_no_qc(self):
        # Sample dataframe without 'DART_quality_control' column
        data = {
            "latitude": [10.0, 20.0, 30.0],
            "longitude": [40.0, 50.0, 60.0],
            "type": ["ACARS_TEMPERATURE", "RADIOSONDE_U_WIND_COMPONENT", "ACARS_TEMPERATURE"],
            "observation": [1.0, 2.0, 3.0],
            "obs_num": [1001, 1002, 1003],
        }
        df = pd.DataFrame(data)

        # Create an instance of obs_sequence with the sample DataFrame
        obs_seq_no_qc = obsq.ObsSequence(file=None)
        obs_seq_no_qc.df = df
        return obs_seq_no_qc

    def test_geo_plot_with_qc(self, obs_seq):
        fig = ip.geo_plot(obs_seq)
        # Check that a figure is returned
        assert fig is not None
        # Check that the hover template includes 'DART_quality_control'
        assert "DART_quality_control" in fig.data[0].hovertemplate
        # Check that the figure has data
        assert len(fig.data) > 0

    def test_geo_plot_without_qc(self, obs_seq_no_qc):
        fig = ip.geo_plot(obs_seq_no_qc)
        # Check that a figure is returned
        assert fig is not None
        # Check that the hover template includes 'DART_quality_control'
        assert "DART_quality_control" not in fig.data[0].hovertemplate
        # Check that the figure has data
        assert len(fig.data) > 0

class TestDashApps:
    @pytest.fixture
    def obs_seq(self):
        # Sample dataframe for testing
        data = {
            "latitude": [10.0, 20.0, 30.0],
            "longitude": [40.0, 50.0, 60.0],
            "type": ["ACARS_TEMPERATURE", "RADIOSONDE_U_WIND_COMPONENT", "ACARS_TEMPERATURE"],
            "observation": [1.0, 2.0, 3.0],
            "obs_num": [1001, 1002, 1003],
            "DART_quality_control": [0, 1, 2]
        }
        df = pd.DataFrame(data)

        # Create an instance of obs_sequence with the sample DataFrame
        obs_seq = obsq.ObsSequence(file=None)
        obs_seq.df = df
        return obs_seq

    def test_include_only_selected_obs_dash_app(self, obs_seq):
        # Create a copy of the obs_seq for selection
        obs_seq_selected = obsq.ObsSequence(file=None)
        obs_seq_selected.df = obs_seq.df.copy()

        # Create the figure for the Dash app
        fig = ip.geo_plot(obs_seq)
        app = ip.include_only_selected_obs_dash_app(fig, obs_seq_selected)

        # Simulate selecting observations
        selected_data = {"points": [{"customdata": [10.0, "ACARS_TEMPERATURE", 1001]}]}

        predetermined_output_selected_data = [
            "Total number of observations selected: ",
            1,
            "\n\nTypes of observations selected: ",
            "[\n  \"ACARS_TEMPERATURE\"\n]",
            "\n\nSelected observations (obs_num): ",
            "[\n  1001\n]"
            ]
        predetermined_output_store = [1001]

        # Use the callback map to get the output from get_selected_data
        callback = app.callback_map["..selected-data.children...store.data.."]["callback"]
        outputs_list = [{"id": "selected-data", "property": "children"}, {"id": "store", "property": "data"}]
        full_output = callback(selected_data, outputs_list=outputs_list)
        output_json = json.loads(full_output)

        # Verify selected-data and store outputs
        assert(output_json["response"]["selected-data"]["children"] == predetermined_output_selected_data)
        assert(output_json["response"]["store"]["data"] == predetermined_output_store)

    def test_exclude_selected_obs_dash_app(self, obs_seq):
        # Create a copy of the obs_seq for selection
        obs_seq_selected = obsq.ObsSequence(file=None)
        obs_seq_selected.df = obs_seq.df.copy()

        # Create the figure for the Dash app
        fig = ip.geo_plot(obs_seq)
        app = ip.exclude_selected_obs_dash_app(fig, obs_seq_selected)

        # Simulate selecting observations
        selected_data = {"points": [{"customdata": [10.0, "ACARS_TEMPERATURE", 1001]}]}

        predetermined_output_selected_data = [
            "Total number of observations selected: ",
            1,
            "\n\nTypes of observations selected: ",
            "[\n  \"ACARS_TEMPERATURE\"\n]",
            "\n\nSelected observations (obs_num): ",
            "[\n  1001\n]"
            ]
        predetermined_output_store = [1001]

        # Use the callback map to get the output from get_selected_data
        callback = app.callback_map["..selected-data.children...store.data.."]["callback"]
        outputs_list = [{"id": "selected-data", "property": "children"}, {"id": "store", "property": "data"}]
        full_output = callback(selected_data, outputs_list=outputs_list)
        output_json = json.loads(full_output)

        # Verify selected-data and store outputs
        assert(output_json["response"]["selected-data"]["children"] == predetermined_output_selected_data)
        assert(output_json["response"]["store"]["data"] == predetermined_output_store)