# SPDX-License-Identifier: Apache-2.0
import os
import pytest
import tempfile
import datetime as dt
import pandas as pd
from pydartdiags.obs_sequence import obs_sequence as obsq
from pydartdiags.stats import stats
import numpy as np
import yaml


class TestConvertDartTime:
    def test_case1(self):
        result = obsq.convert_dart_time(0, 0)
        expected = dt.datetime(1601, 1, 1)
        assert result == expected

    def test_case2(self):
        result = obsq.convert_dart_time(86400, 0)
        expected = dt.datetime(1601, 1, 2)
        assert result == expected

    def test_case3(self):
        result = obsq.convert_dart_time(0, 1)
        expected = dt.datetime(1601, 1, 2)
        assert result == expected

    def test_case4(self):
        result = obsq.convert_dart_time(2164, 151240)
        expected = dt.datetime(2015, 1, 31, 0, 36, 4)
        assert result == expected


class TestSanitizeInput:
    @pytest.fixture
    def bad_loc_file_path(self):
        test_dir = os.path.dirname(__file__)
        return os.path.join(test_dir, "data", "obs_seq.invalid_loc")

    def test_catch_bad_loc(self, bad_loc_file_path):
        with pytest.raises(
            ValueError,
            match="Neither 'loc3d' nor 'loc1d' could be found in the observation sequence.",
        ):
            obj = obsq.obs_sequence(bad_loc_file_path)


class TestOneDimensional:
    @pytest.fixture
    def obs_seq_file_path(self):
        test_dir = os.path.dirname(__file__)
        return os.path.join(test_dir, "data", "obs_seq.1d.final")

    def test_read1d(self, obs_seq_file_path):
        obj = obsq.obs_sequence(obs_seq_file_path)
        assert obj.loc_mod == "loc1d"
        assert len(obj.df) == 40  # 40 obs in the file
        assert (
            obj.df.columns.str.contains("posterior").sum() == 22
        )  # 20 members + mean + spread
        assert obj.df.columns.str.contains("prior").sum() == 22


class TestSynonyms:
    @pytest.fixture
    def synonym_file_path(self):
        test_dir = os.path.dirname(__file__)
        return os.path.join(test_dir, "data", "obs_seq.final.ascii.syn")

    def test_single(self, synonym_file_path):
        obj1 = obsq.obs_sequence(synonym_file_path, synonyms="observationx")
        assert "observationx" in obj1.synonyms_for_obs

    def test_list(self, synonym_file_path):
        obj2 = obsq.obs_sequence(
            synonym_file_path, synonyms=["synonym1", "synonym2", "observationx"]
        )
        assert "synonym1" in obj2.synonyms_for_obs
        assert "synonym2" in obj2.synonyms_for_obs


class TestBinaryObsSequence:
    @pytest.fixture
    def binary_obs_seq_file_path(self):
        test_dir = os.path.dirname(__file__)
        return os.path.join(test_dir, "data", "obs_seq.final.binary.small")

    def test_read_binary(self, binary_obs_seq_file_path):
        obj = obsq.obs_sequence(binary_obs_seq_file_path)
        assert len(obj.df) > 0  # Ensure the DataFrame is not empty


class TestWriteAscii:
    @pytest.fixture
    def ascii_obs_seq_file_path(self):
        test_dir = os.path.dirname(__file__)
        return os.path.join(test_dir, "data", "obs_seq.final.ascii.small")

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield tmpdirname

    def normalize_whitespace(self, line):
        return "".join(line.split())

    def compare_files_line_by_line(self, file1, file2):
        """
        Compare two files line by line, ensuring that they have the same content.

        This function reads two files line by line, splits each line into components,
        and compares each component. If the components can be converted to floats,
        they are compared as floats. If the conversion fails, the components are
        compared as strings after normalizing whitespace. The function also ensures
        that both files have the same number of lines.

        Args:
            file1 (str): Path to the first file to compare.
            file2 (str): Path to the second file to compare.

        Raises:
            AssertionError: If the files have different numbers of components on any line,
                            if any corresponding components differ, or if the files have
                            different numbers of lines.
        """
        with open(file1, "r") as f1, open(file2, "r") as f2:
            for line1, line2 in zip(f1, f2):
                components1 = line1.split()
                components2 = line2.split()

                assert len(components1) == len(
                    components2
                ), f"Different number of components:\n{line1}\n{line2}"

                for comp1, comp2 in zip(components1, components2):
                    try:
                        # Attempt to convert to float and compare
                        assert float(comp1) == float(
                            comp2
                        ), f"Difference found:\n{line1}\n{line2}"
                    except ValueError:
                        # If conversion fails, normalize whitespace and compare as strings
                        normalized_comp1 = self.normalize_whitespace(comp1)
                        normalized_comp2 = self.normalize_whitespace(comp2)
                        assert (
                            normalized_comp1 == normalized_comp2
                        ), f"Difference found:\n{line1}\n{line2}"

        # Ensure both files have the same number of lines
        with open(file1, "r") as f1, open(file2, "r") as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()
            assert len(lines1) == len(lines2), "Files have different number of lines"

    @pytest.mark.parametrize(
        "ascii_obs_seq_file_path",
        [
            os.path.join(
                os.path.dirname(__file__), "data", "obs_seq.final.ascii.small"
            ),
            os.path.join(os.path.dirname(__file__), "data", "obs_seq.final.post.small"),
            os.path.join(
                os.path.dirname(__file__), "data", "obs_seq.final.ascii.test_meta"
            ),
            os.path.join(os.path.dirname(__file__), "data", "obs_seq.1d.final"),
            os.path.join(os.path.dirname(__file__), "data", "obs_seq.out.GSI.small"),
        ],
    )
    def test_write_ascii(self, ascii_obs_seq_file_path, temp_dir):
        # Create a temporary file path for the output
        temp_output_file_path = os.path.join(temp_dir, "obs_seq.final.ascii.write")

        # Create an instance of the obs_sequence class and write the output file
        obj = obsq.obs_sequence(ascii_obs_seq_file_path)
        obj.write_obs_seq(temp_output_file_path)

        # Ensure the output file exists
        assert os.path.exists(temp_output_file_path)

        # Compare the written file with the reference file, line by line
        self.compare_files_line_by_line(temp_output_file_path, ascii_obs_seq_file_path)

        # Clean up is handled by the temporary directory context manager

    @pytest.mark.parametrize(
        "obs_seq_file_path",
        [
            os.path.join(
                os.path.dirname(__file__), "data", "obs_seq.final.ascii.small"
            ),
            os.path.join(os.path.dirname(__file__), "data", "obs_seq.out.GSI.small"),
        ],
    )
    def test_write_after_stats(self, obs_seq_file_path, temp_dir):
        # Create a temporary file path for the output
        temp_output_file_path = os.path.join(
            temp_dir, "obs_seq.final.ascii.write-after-stats"
        )

        # Create an instance of the obs_sequence class and write the output file
        obj = obsq.obs_sequence(obs_seq_file_path)
        stats.diag_stats(obj.df)  # add the stats columns
        obj.write_obs_seq(temp_output_file_path)

        # Ensure the output file exists
        assert os.path.exists(temp_output_file_path)

        # Compare the written file with the reference file, line by line
        self.compare_files_line_by_line(temp_output_file_path, obs_seq_file_path)

        # Clean up is handled by the temporary directory context manager

    @pytest.mark.parametrize(
        "obs_seq_file_path",
        [
            os.path.join(
                os.path.dirname(__file__), "data", "obs_seq.final.ascii.small"
            ),
            os.path.join(os.path.dirname(__file__), "data", "obs_seq.out.GSI.small"),
        ],
    )
    def test_write_after_bin(self, obs_seq_file_path, temp_dir):
        # Create a temporary file path for the output
        temp_output_file_path = os.path.join(
            temp_dir, "obs_seq.final.ascii.write-after-bin"
        )

        # Create an instance of the obs_sequence class and write the output file
        obj = obsq.obs_sequence(obs_seq_file_path)
        hPalevels = [
            0.0,
            100.0,
            150.0,
            200.0,
            250.0,
            300.0,
            400.0,
            500.0,
            700,
            850,
            925,
            1000,
        ]  # hPa
        levels = [i * 100 for i in hPalevels]
        stats.bin_by_layer(obj.df, levels)  # add the stats columns
        obj.write_obs_seq(temp_output_file_path)

        # Ensure the output file exists
        assert os.path.exists(temp_output_file_path)

        # Compare the written file with the reference file, line by line
        self.compare_files_line_by_line(temp_output_file_path, obs_seq_file_path)

        # Clean up is handled by the temporary directory context manager

    def test_write_after_remove_obs(self, temp_dir):
        # Create a temporary file path for the output
        temp_output_file_path = os.path.join(
            temp_dir, "obs_seq.final.ascii.write-after-remove-obs"
        )

        # Create an instance of the obs_sequence class
        obs_seq_file_path = os.path.join(
            os.path.dirname(__file__), "data", "obs_seq.final.ascii.small"
        )
        obj = obsq.obs_sequence(obs_seq_file_path)

        # Remove obs except ACARS_TEMPERATURE
        obj.df = obj.df[(obj.df["type"] == "ACARS_TEMPERATURE")]

        # Write the output file
        obj.write_obs_seq(temp_output_file_path)

        # Ensure the output file exists
        assert os.path.exists(temp_output_file_path)

        reference_file_path = os.path.join(
            os.path.dirname(__file__), "data", "only_acars.final"
        )

        # Compare the written file with the reference file, line by line
        self.compare_files_line_by_line(temp_output_file_path, reference_file_path)


class TestObsDataframe:
    @pytest.fixture
    def obs_seq(self):
        # Create a sample DataFrame to simulate the observation sequence
        data = {
            "DART_quality_control": [0, 1, 2, 0, 3, 0],
            "type": ["type1", "type2", "type1", "type3", "type2", "type1"],
            "observation": [1.0, 2.0, 3.0, 4.0, 5.0, 5.2],
            "prior_ensemble_mean": [1.1, 2.1, 3.1, 4.1, 5.1, 5.3],
            "prior_ensemble_spread": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
        }
        df = pd.DataFrame(data)

        # Create an instance of ObsSequence with the sample DataFrame
        obs_seq = obsq.obs_sequence(file=None)
        obs_seq.df = df
        return obs_seq

    def test_select_by_dart_qc(self, obs_seq):
        dart_qc_value = 2
        result = obs_seq.select_by_dart_qc(dart_qc_value).reset_index(drop=True)

        # Expected DataFrame
        expected_data = {
            "DART_quality_control": [2],
            "type": ["type1"],
            "observation": [3.0],
            "prior_ensemble_mean": [3.1],
            "prior_ensemble_spread": [0.3],
        }
        expected_df = pd.DataFrame(expected_data)

        # Assert that the result matches the expected DataFrame, ignoring the index
        pd.testing.assert_frame_equal(result, expected_df)

    def test_select_used_qcs(self, obs_seq):
        result = obs_seq.select_used_qcs().reset_index(drop=True)

        # Expected DataFrame
        expected_data = {
            "DART_quality_control": [0, 2, 0, 0],
            "type": ["type1", "type1", "type3", "type1"],
            "observation": [1.0, 3.0, 4.0, 5.2],
            "prior_ensemble_mean": [1.1, 3.1, 4.1, 5.3],
            "prior_ensemble_spread": [0.1, 0.3, 0.4, 0.6],
        }
        expected_df = pd.DataFrame(expected_data)

        # Assert that the result matches the expected DataFrame, ignoring the index
        pd.testing.assert_frame_equal(result, expected_df)

    def test_possible_vs_used(self, obs_seq):
        result = obs_seq.possible_vs_used()

        # Expected DataFrame
        expected_data = {
            "type": ["type1", "type2", "type3"],
            "possible": [3, 2, 1],
            "used": [3, 0, 1],
        }
        expected_df = pd.DataFrame(expected_data)

        # Assert that the result matches the expected DataFrame, ignoring the index
        pd.testing.assert_frame_equal(result, expected_df)


class TestJoin:
    @pytest.fixture
    def obs_seq1d_file_path(self):
        test_dir = os.path.dirname(__file__)
        return os.path.join(test_dir, "data", "obs_seq.1d.final")

    @pytest.fixture
    def binary_obs_seq_file_path(self):
        test_dir = os.path.dirname(__file__)
        return os.path.join(test_dir, "data", "obs_seq.final.binary.small")

    @pytest.fixture
    # 10 obs
    def ascii_obs_seq_file_path1(self):
        test_dir = os.path.dirname(__file__)
        return os.path.join(test_dir, "data", "obs_seq.final.ascii.small")

    @pytest.fixture
    # 3 obs
    def ascii_obs_seq_file_path2(self):
        test_dir = os.path.dirname(__file__)
        return os.path.join(test_dir, "data", "obs_seq.final.ascii.small.more-types")

    @pytest.fixture
    # 3 obs
    def ascii_obs_seq_file_path3(self):
        test_dir = os.path.dirname(__file__)
        return os.path.join(
            test_dir, "data", "obs_seq.final.ascii.small.not-so-many-types"
        )

    @pytest.fixture
    def ascii_obs_seq_file_path4(self):
        test_dir = os.path.dirname(__file__)
        return os.path.join(
            test_dir, "data", "obs_seq.final.ascii.small.not-so-many-copies"
        )

    def is_reverse_dict(self, dict1, dict2):
        return {v: k for k, v in dict1.items()} == dict2

    def test_empty_list(self):
        with pytest.raises(
            ValueError, match="The list of observation sequences is empty."
        ):
            obsq.obs_sequence.join([])

    def test_join_diff_locs(self, obs_seq1d_file_path, binary_obs_seq_file_path):
        obj1 = obsq.obs_sequence(obs_seq1d_file_path)
        obj2 = obsq.obs_sequence(binary_obs_seq_file_path)
        with pytest.raises(
            ValueError, match="All observation sequences must have the same loc_mod."
        ):
            obsq.obs_sequence.join([obj1, obj2])

    def test_join_three_obs_seqs(
        self,
        ascii_obs_seq_file_path1,
        ascii_obs_seq_file_path2,
        ascii_obs_seq_file_path3,
    ):
        obj1 = obsq.obs_sequence(ascii_obs_seq_file_path1)
        obj2 = obsq.obs_sequence(ascii_obs_seq_file_path2)
        obj3 = obsq.obs_sequence(ascii_obs_seq_file_path3)
        obs_seq_mega = obsq.obs_sequence.join([obj1, obj2, obj3])

        assert obs_seq_mega.all_obs == None
        assert len(obs_seq_mega.df) == 16  # obs in the dataframe
        assert obs_seq_mega.loc_mod == "loc3d"
        assert obs_seq_mega.has_assimilation_info() == True
        assert obs_seq_mega.has_posterior() == False
        assert list(obs_seq_mega.types.keys()) == list(range(1, 26))  # 25 obs types
        obs_types = [
            "AIRCRAFT_TEMPERATURE",
            "BLUE_LAND_SFC_ALTIMETER",
            "MARINE_SFC_SPECIFIC_HUMIDITY",
            "SAT_V_WIND_COMPONENT",
            "RADIOSONDE_SPECIFIC_HUMIDITY",
            "MARINE_SFC_TEMPERATURE",
            "RADIOSONDE_U_WIND_COMPONENT",
            "MARINE_SFC_ALTIMETER",
            "AIRCRAFT_V_WIND_COMPONENT",
            "RADIOSONDE_SURFACE_ALTIMETER",
            "ACARS_TEMPERATURE",
            "LAND_SFC_ALTIMETER",
            "MARINE_SFC_V_WIND_COMPONENT",
            "AIRS_TEMPERATURE",
            "GPSRO_REFRACTIVITY",
            "MARINE_SFC_U_WIND_COMPONENT",
            "ACARS_U_WIND_COMPONENT",
            "RADIOSONDE_V_WIND_COMPONENT",
            "SAT_U_WIND_COMPONENT",
            "GREEN_LAND_SFC_ALTIMETER",
            "ACARS_V_WIND_COMPONENT",
            "RADIOSONDE_TEMPERATURE",
            "AIRCRAFT_U_WIND_COMPONENT",
            "AIRS_SPECIFIC_HUMIDITY",
            "PINK_LAND_SFC_ALTIMETER",
        ]
        all_obs_present = all(
            value in obs_seq_mega.types.values() for value in obs_types
        )
        assert all_obs_present
        assert self.is_reverse_dict(obs_seq_mega.types, obs_seq_mega.reverse_types)

    def test_join_list_sub_copies(
        self, ascii_obs_seq_file_path1, ascii_obs_seq_file_path3
    ):
        obj1 = obsq.obs_sequence(ascii_obs_seq_file_path1)
        obj3 = obsq.obs_sequence(ascii_obs_seq_file_path3)
        obs_seq_mega = obsq.obs_sequence.join(
            [obj1, obj3], ["prior_ensemble_mean", "observation", "Data_QC"]
        )

        assert obs_seq_mega.n_non_qc == 2
        assert obs_seq_mega.n_qc == 1
        assert obs_seq_mega.n_copies == 3
        assert obs_seq_mega.copie_names == [
            "observation",
            "prior_ensemble_mean",
            "Data_QC",
        ]  # order is important

    def test_join_list_sub_copies_no_qc(
        self, ascii_obs_seq_file_path1, ascii_obs_seq_file_path3
    ):
        obj1 = obsq.obs_sequence(ascii_obs_seq_file_path1)
        obj3 = obsq.obs_sequence(ascii_obs_seq_file_path3)
        obs_seq_mega = obsq.obs_sequence.join(
            [obj1, obj3], ["observation", "prior_ensemble_spread"]
        )

        assert obs_seq_mega.n_non_qc == 2
        assert obs_seq_mega.n_qc == 0
        assert obs_seq_mega.n_copies == 2
        assert obs_seq_mega.copie_names == ["observation", "prior_ensemble_spread"]

    def test_join_copies_not_in_all(
        self, ascii_obs_seq_file_path1, ascii_obs_seq_file_path4
    ):
        obj1 = obsq.obs_sequence(ascii_obs_seq_file_path1)
        obj4 = obsq.obs_sequence(ascii_obs_seq_file_path4)
        with pytest.raises(
            ValueError, match="All observation sequences must have the same copies."
        ):
            obsq.obs_sequence.join([obj1, obj4])

    def test_join_copies_not_all_have_subset(
        self, ascii_obs_seq_file_path1, ascii_obs_seq_file_path4
    ):
        obj1 = obsq.obs_sequence(ascii_obs_seq_file_path1)
        obj4 = obsq.obs_sequence(ascii_obs_seq_file_path4)
        with pytest.raises(
            ValueError, match="All observation sequences must have the selected copies."
        ):
            obsq.obs_sequence.join([obj1, obj4], ["prior_ensemble_member_41"])

    def test_join_list_sub_copies(
        self, ascii_obs_seq_file_path1, ascii_obs_seq_file_path3
    ):
        obj1 = obsq.obs_sequence(ascii_obs_seq_file_path1)
        obj3 = obsq.obs_sequence(ascii_obs_seq_file_path3)
        obs_seq_mega = obsq.obs_sequence.join(
            [obj1, obj3], ["prior_ensemble_mean", "observation", "Data_QC"]
        )
        assert obs_seq_mega.has_assimilation_info() == False
        assert obs_seq_mega.has_posterior() == False


class TestCreateHeader:
    def test_create_header(self):
        obj = obsq.obs_sequence(file=None)

        obj.types = {1: "ACARS_BELLYBUTTON", 2: "NCEP_TOES"}
        obj.n_non_qc = 2
        obj.n_qc = 1
        obj.n_copies = obj.n_non_qc + obj.n_qc
        obj.copie_names = ["observation", "mean", "qc"]

        n = 5  # max_num_obs, size of dataframe
        obj.create_header(n)

        # Define the expected header
        expected_header = [
            "obs_sequence",
            "obs_type_definitions",
            "2",
            "1 ACARS_BELLYBUTTON",
            "2 NCEP_TOES",
            "num_copies: 2  num_qc: 1",
            "num_obs: 5  max_num_obs: 5",
            "observation",
            "mean",
            "qc",
            "first: 1 last: 5",
        ]
        assert obj.header == expected_header


class TestSplitMetadata:
    def test_split_metadata_with_external_FO(self):
        metadata = ["meta1", "meta2", "external_FO1", "meta3", "meta4"]
        before_external_FO, after_external_FO = obsq.obs_sequence.split_metadata(
            metadata
        )
        assert before_external_FO == ["meta1", "meta2"]
        assert after_external_FO == ["external_FO1", "meta3", "meta4"]

    def test_split_metadata_without_external_FO(self):
        metadata = ["meta1", "meta2", "meta3", "meta4"]
        before_external_FO, after_external_FO = obsq.obs_sequence.split_metadata(
            metadata
        )
        assert before_external_FO == ["meta1", "meta2", "meta3", "meta4"]
        assert after_external_FO == []

    def test_split_metadata_multiple_external_FO(self):
        metadata = ["meta1", "external_FO1", "meta2", "external_FO2", "meta3"]
        before_external_FO, after_external_FO = obsq.obs_sequence.split_metadata(
            metadata
        )
        assert before_external_FO == ["meta1"]
        assert after_external_FO == ["external_FO1", "meta2", "external_FO2", "meta3"]

    def test_split_metadata_empty_list(self):
        metadata = []
        before_external_FO, after_external_FO = obsq.obs_sequence.split_metadata(
            metadata
        )
        assert before_external_FO == []
        assert after_external_FO == []

    def test_split_metadata_no_external_FO(self):
        metadata = ["meta1", "meta2", "meta3"]
        before_external_FO, after_external_FO = obsq.obs_sequence.split_metadata(
            metadata
        )
        assert before_external_FO == ["meta1", "meta2", "meta3"]
        assert after_external_FO == []

    def test_split_metadata_external_FO_at_start(self):
        metadata = ["external_FO1", "meta1", "meta2"]
        before_external_FO, after_external_FO = obsq.obs_sequence.split_metadata(
            metadata
        )
        assert before_external_FO == []
        assert after_external_FO == ["external_FO1", "meta1", "meta2"]

    def test_split_metadata_external_FO_at_end(self):
        metadata = ["meta1", "meta2", "external_FO1"]
        before_external_FO, after_external_FO = obsq.obs_sequence.split_metadata(
            metadata
        )
        assert before_external_FO == ["meta1", "meta2"]
        assert after_external_FO == ["external_FO1"]


class TestGenerateLinkedListPattern:
    def test_generate_linked_list_pattern(self):
        n = 1
        expected_pattern = ["0           -1         -1"]
        result = obsq.obs_sequence.generate_linked_list_pattern(n)
        assert result == expected_pattern

        n = 3
        expected_pattern = [
            "-1          2          -1",
            "1           3          -1",
            "2           -1         -1",
        ]
        result = obsq.obs_sequence.generate_linked_list_pattern(n)
        assert result == expected_pattern

        n = 6
        expected_pattern = [
            "-1          2          -1",
            "1           3          -1",
            "2           4          -1",
            "3           5          -1",
            "4           6          -1",
            "5           -1         -1",
        ]
        result = obsq.obs_sequence.generate_linked_list_pattern(n)
        assert result == expected_pattern


class TestCreateHeaderFromDataFrame:
    @pytest.fixture
    def obs_seq(self):
        # Create a sample DataFrame for testing - some columns are not used in the header
        data = {
            "type": [
                "ACARS_TEMPERATURE",
                "ACARS_TEMPERATURE",
                "RADIOSONDE_U_WIND_COMPONENT",
            ],
            "latitude": [10.0, 20.0, 30.0],
            "longitude": [40.0, 50.0, 60.0],
            "vertical": [100.0, 200.0, 300.0],
            "observation": [1.0, 2.0, 3.0],
            "prior_ensemble_mean": [1.1, 2.1, 3.1],
            "prior_ensemble_spread": [0.1, 0.2, 0.3],
            "posterior_ensemble_mean": [1.2, 2.2, 3.2],
            "posterior_ensemble_spread": [0.2, 0.3, 0.4],
            "DART_quality_control": [0, 1, 2],
            "obs_err_var": [0.01, 0.02, 0.03],
            "linked_list": [
                "-1          2          -1",
                "1           3          -1",
                "2           -1         -1",
            ],
            "posterior_sq_err": [0.04, 0.05, 0.06],
        }
        df = pd.DataFrame(data)

        # Create an instance of obs_sequence with the sample DataFrame
        obs_seq = obsq.obs_sequence(file=None)
        obs_seq.df = df
        obs_seq.reverse_types = {
            "ACARS_TEMPERATURE": 1,
            "RADIOSONDE_U_WIND_COMPONENT": 2,
        }
        obs_seq.n_non_qc = 4
        obs_seq.n_qc = 1
        return obs_seq

    def test_create_header_from_dataframe(self, obs_seq):
        # Call the method to create the header
        obs_seq.create_header_from_dataframe()

        # Verify the header is correctly created
        expected_header = [
            "obs_sequence",
            "obs_type_definitions",
            "2",
            "1 ACARS_TEMPERATURE",
            "2 RADIOSONDE_U_WIND_COMPONENT",
            "num_copies: 4  num_qc: 1",
            "num_obs:          3 max_num_obs:          3",
            "observation",
            "prior ensemble mean",
            "prior ensemble spread",
            "posterior ensemble mean",
            "posterior ensemble spread",
            "DART quality control",
            "first:            1 last:            3",
        ]

        assert expected_header == obs_seq.header


class TestUpdateTypesDicts:
    @pytest.fixture
    def sample_df(self):
        data = {
            "type": [
                "ACARS_TEMPERATURE",
                "ACARS_TEMPERATURE",
                "RADIOSONDE_U_WIND_COMPONENT",
                "PINEAPPLE_COUNT",
            ],
            "latitude": [10.0, 20.0, 30.0, 40.0],
            "longitude": [40.0, 50.0, 60.0, 70.0],
            "vertical": [100.0, 200.0, 300.0, 400.0],
            "time": [1000, 2000, 3000, 4000],
            "observation": [1.0, 2.0, 3.0, 4.0],
            "obs_err_var": [0.01, 0.02, 0.03, 0.04],
        }
        return pd.DataFrame(data)

    def test_update_types_dicts(self, sample_df):
        reverse_types = {"ACARS_TEMPERATURE": "32", "RADIOSONDE_U_WIND_COMPONENT": "51"}
        expected_reverse_types = {
            "ACARS_TEMPERATURE": "32",
            "RADIOSONDE_U_WIND_COMPONENT": "51",
            "PINEAPPLE_COUNT": "52",
        }
        expected_types = {
            "32": "ACARS_TEMPERATURE",
            "51": "RADIOSONDE_U_WIND_COMPONENT",
            "52": "PINEAPPLE_COUNT",
        }

        updated_reverse_types, types = obsq.obs_sequence.update_types_dicts(
            sample_df, reverse_types
        )

        assert updated_reverse_types == expected_reverse_types
        assert types == expected_types


class TestCompositeTypes:
    @pytest.fixture
    def obs_seq(self):
        test_dir = os.path.dirname(__file__)
        file_path = os.path.join(test_dir, "data", "three-obs.final")

        # Create an instance of obs_sequence with the 'three-obs.final' file
        obs_seq = obsq.obs_sequence(file_path)
        return obs_seq

    @pytest.mark.parametrize(
        "composite_types_arg",
        [
            None,
            "use_default",
            os.path.join(os.path.dirname(__file__), "data", "composite_acars.yaml"),
        ],
    )
    def test_composite_types(self, obs_seq, composite_types_arg):

        # Save the original DataFrame for comparison
        orig_df = obs_seq.df.copy()
        # Call the composite_types method
        if composite_types_arg is None:
            obs_seq.composite_types()
        else:
            obs_seq.composite_types(composite_types=composite_types_arg)

        # Verify composite types added to the DataFrame
        types = obs_seq.df["type"].unique()
        expected_composite_types = [
            "ACARS_TEMPERATURE",
            "ACARS_U_WIND_COMPONENT",
            "ACARS_V_WIND_COMPONENT",
            "ACARS_HORIZONTAL_WIND",
        ]

        assert len(types) == len(expected_composite_types)
        for type in expected_composite_types:
            assert type in types

        # Verify that the columns themselves are unchanged
        assert obs_seq.df.columns.equals(
            orig_df.columns
        ), f"Columns changed: {obs_seq.df.columns}"

        # Verify composite types are correctly calculated
        prior_columns = obs_seq.df.filter(regex="prior_ensemble").columns.tolist()
        posterior_columns = obs_seq.df.filter(
            regex="posterior_ensemble"
        ).columns.tolist()
        combo_cols = ["observation", "obs_err_var"] + prior_columns + posterior_columns

        for col in combo_cols:
            u_wind = obs_seq.df.loc[
                obs_seq.df["type"] == "ACARS_U_WIND_COMPONENT", col
            ].values[0]
            v_wind = obs_seq.df.loc[
                obs_seq.df["type"] == "ACARS_V_WIND_COMPONENT", col
            ].values[0]
            wind = obs_seq.df.loc[
                obs_seq.df["type"] == "ACARS_HORIZONTAL_WIND", col
            ].values[0]
            assert np.isclose(
                np.sqrt(u_wind**2 + v_wind**2), wind
            ), f"Mismatch in column {col}: {wind} != sqrt({u_wind}^2 + {v_wind}^2)"

        # Verify that the non-composite columns are unchanged
        for col in obs_seq.df.columns:
            if col not in combo_cols:
                assert (
                    obs_seq.df.loc[
                        obs_seq.df["type"] == "ACARS_U_WIND_COMPONENT", col
                    ].values[0]
                    == orig_df.loc[
                        orig_df["type"] == "ACARS_U_WIND_COMPONENT", col
                    ].values[0]
                )
                assert (
                    obs_seq.df.loc[
                        obs_seq.df["type"] == "ACARS_V_WIND_COMPONENT", col
                    ].values[0]
                    == orig_df.loc[
                        orig_df["type"] == "ACARS_V_WIND_COMPONENT", col
                    ].values[0]
                )

        # Horizontal wind not in original, should be the same as the component
        for col in obs_seq.df.columns:
            if col not in combo_cols and col != "type":
                assert (
                    obs_seq.df.loc[
                        obs_seq.df["type"] == "ACARS_HORIZONTAL_WIND", col
                    ].values[0]
                    == obs_seq.df.loc[
                        obs_seq.df["type"] == "ACARS_U_WIND_COMPONENT", col
                    ].values[0]
                )

        # Verify that the non-composite types are unchanged for all columns
        for col in obs_seq.df.columns:
            assert (
                obs_seq.df.loc[obs_seq.df["type"] == "ACARS_TEMPERATURE", col].values[0]
                == orig_df.loc[orig_df["type"] == "ACARS_TEMPERATURE", col].values[0]
            )

    def test_composite_types_dups(self):
        test_dir = os.path.dirname(__file__)
        file_path = os.path.join(test_dir, "data", "dups-obs.final")

        dup = obsq.obs_sequence(file_path)
        # Test that composite_types raises an error
        with pytest.raises(Exception, match="There are duplicates in the components."):
            dup.composite_types()

    def test_no_yaml_file(self):
        with pytest.raises(Exception):
            obsq.load_yaml_to_dict("nonexistent.yaml")

    def test_load_yaml_to_dict_broken_file(self, tmpdir):
        # Create a broken YAML file
        broken_yaml_content = """
        composite_types:
          ACARS_HORIZONTAL_WIND:
            components: [ACARS_U_WIND_COMPONENT, ACARS_V_WIND_COMPONENT
        """
        broken_file = tmpdir.join("broken_composite_types.yaml")
        with open(broken_file, "w") as f:
            f.write(broken_yaml_content)

        # Test that load_yaml_to_dict raises an exception for the broken YAML file
        with pytest.raises(yaml.YAMLError):
            obsq.load_yaml_to_dict(broken_file)


if __name__ == "__main__":
    pytest.main()
