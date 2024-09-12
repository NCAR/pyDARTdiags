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

if __name__ == '__main__':
    pytest.main()