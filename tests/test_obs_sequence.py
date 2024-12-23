import os
import pytest
import tempfile
import filecmp
import datetime as dt
import pandas as pd
from pydartdiags.obs_sequence import obs_sequence as obsq

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
        return os.path.join(test_dir, 'data', 'obs_seq.invalid_loc')

    def test_catch_bad_loc(self, bad_loc_file_path):
        with pytest.raises(ValueError, match="Neither 'loc3d' nor 'loc1d' could be found in the observation sequence."):
            obj = obsq.obs_sequence(bad_loc_file_path)

class TestOneDimensional:
    @pytest.fixture
    def obs_seq_file_path(self):
        test_dir = os.path.dirname(__file__)
        return os.path.join(test_dir, 'data', 'obs_seq.1d.final')
      
    def test_read1d(self, obs_seq_file_path):
        obj = obsq.obs_sequence(obs_seq_file_path)
        assert obj.loc_mod == 'loc1d'
        assert len(obj.df) == 40  # 40 obs in the file
        assert obj.df.columns.str.contains('posterior').sum() == 24  # 20 members + mean + spread + sq_err + bias
        assert obj.df.columns.str.contains('prior').sum() == 24
 


class TestSynonyms:
    @pytest.fixture
    def synonym_file_path(self):
        test_dir = os.path.dirname(__file__)
        return os.path.join(test_dir, 'data', 'obs_seq.final.ascii.syn')

    def test_missing_key(self, synonym_file_path):
        with pytest.raises(KeyError, match="'observation'"):
            obj3 = obsq.obs_sequence(synonym_file_path)

    def test_single(self, synonym_file_path):
        obj1 = obsq.obs_sequence(synonym_file_path, synonyms="observationx")
        assert "observationx" in obj1.synonyms_for_obs

    def test_list(self, synonym_file_path):
        obj2 = obsq.obs_sequence(synonym_file_path, synonyms=["synonym1", "synonym2", "observationx"])
        assert "synonym1" in obj2.synonyms_for_obs
        assert "synonym2" in obj2.synonyms_for_obs

    def test_missing_key_per_instance(self, synonym_file_path):
        with pytest.raises(KeyError, match="'observation'"):
            obj3 = obsq.obs_sequence(synonym_file_path)
            
class TestBinaryObsSequence:
    @pytest.fixture
    def binary_obs_seq_file_path(self):
        test_dir = os.path.dirname(__file__)
        return os.path.join(test_dir, 'data', 'obs_seq.final.binary.small')

    def test_read_binary(self, binary_obs_seq_file_path):
        obj = obsq.obs_sequence(binary_obs_seq_file_path)
        assert len(obj.df) > 0  # Ensure the DataFrame is not empty

class TestWriteAscii:
    @pytest.fixture
    def ascii_obs_seq_file_path(self):
        test_dir = os.path.dirname(__file__)
        return os.path.join(test_dir, 'data', 'obs_seq.final.ascii.small')

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield tmpdirname

    def normalize_whitespace(self, line):
        return ''.join(line.split())

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
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            for line1, line2 in zip(f1, f2):
                components1 = line1.split()
                components2 = line2.split()
                
                assert len(components1) == len(components2), f"Different number of components:\n{line1}\n{line2}"
                
                for comp1, comp2 in zip(components1, components2):
                    try:
                        # Attempt to convert to float and compare
                        assert float(comp1) == float(comp2), f"Difference found:\n{line1}\n{line2}"
                    except ValueError:
                        # If conversion fails, normalize whitespace and compare as strings
                        normalized_comp1 = self.normalize_whitespace(comp1)
                        normalized_comp2 = self.normalize_whitespace(comp2)
                        assert normalized_comp1 == normalized_comp2, f"Difference found:\n{line1}\n{line2}"

        # Ensure both files have the same number of lines
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()
            assert len(lines1) == len(lines2), "Files have different number of lines"

    @pytest.mark.parametrize("ascii_obs_seq_file_path", [
        os.path.join(os.path.dirname(__file__), 'data', 'obs_seq.final.ascii.small'),
        os.path.join(os.path.dirname(__file__), 'data', 'obs_seq.final.post.small')
    ])
    def test_write_ascii(self, ascii_obs_seq_file_path, temp_dir):
        # Create a temporary file path for the output
        temp_output_file_path = os.path.join(temp_dir, 'obs_seq.final.ascii.write')

        # Create an instance of the obs_sequence class and write the output file
        obj = obsq.obs_sequence(ascii_obs_seq_file_path)
        obj.write_obs_seq(temp_output_file_path)

        # Ensure the output file exists
        assert os.path.exists(temp_output_file_path)

        # Compare the written file with the reference file, line by line
        self.compare_files_line_by_line(temp_output_file_path, ascii_obs_seq_file_path)

        # Clean up is handled by the temporary directory context manager

class TestObsDataframe:
    @pytest.fixture
    def obs_seq(self):
        # Create a sample DataFrame to simulate the observation sequence
        data = {
            'DART_quality_control': [0, 1, 2, 0, 3, 0],
            'type': ['type1', 'type2', 'type1', 'type3', 'type2', 'type1'],
            'observation': [1.0, 2.0, 3.0, 4.0, 5.0, 5.2]
        }
        df = pd.DataFrame(data)
        
        # Create an instance of ObsSequence with the sample DataFrame
        obs_seq = obsq.obs_sequence(file=None)
        obs_seq.df = df
        obs_seq.has_assimilation_info = True  # Set to True for testing purposes
        return obs_seq

    def test_select_by_dart_qc(self, obs_seq):
        dart_qc_value = 2
        result = obs_seq.select_by_dart_qc(dart_qc_value).reset_index(drop=True)
        
        # Expected DataFrame
        expected_data = {
            'DART_quality_control': [2],
            'type': ['type1'],
            'observation': [3.0]
        }
        expected_df = pd.DataFrame(expected_data)
        
        # Assert that the result matches the expected DataFrame, ignoring the index
        pd.testing.assert_frame_equal(result, expected_df)

    def test_select_failed_qcs(self, obs_seq):
        result = obs_seq.select_failed_qcs().reset_index(drop=True)
        
        # Expected DataFrame
        expected_data = {
            'DART_quality_control': [1, 2, 3],
            'type': ['type2', 'type1', 'type2'],
            'observation': [2.0, 3.0, 5.0]
        }
        expected_df = pd.DataFrame(expected_data)
        
        # Assert that the result matches the expected DataFrame, ignoring the index
        pd.testing.assert_frame_equal(result, expected_df)

    def test_possible_vs_used(self, obs_seq):
        result = obs_seq.possible_vs_used()
        
        # Expected DataFrame
        expected_data = {
            'type': ['type1', 'type2', 'type3'],
            'possible': [3, 2, 1],
            'used': [2, 0, 1]
        }
        expected_df = pd.DataFrame(expected_data)
        
        # Assert that the result matches the expected DataFrame, ignoring the index
        pd.testing.assert_frame_equal(result, expected_df)

if __name__ == '__main__':
    pytest.main()