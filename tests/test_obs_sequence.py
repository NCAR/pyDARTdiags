import os
import pytest
import datetime as dt
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
        assert obj.df.columns.str.contains('posterior').sum() == 22 
        assert obj.df.columns.str.contains('prior').sum() == 22
 


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


if __name__ == '__main__':
    pytest.main()