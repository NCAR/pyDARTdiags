import pytest
import datetime as dt
from pydartdiags.obs_sequence import obs_sequence as obsq

def test_convert_dart_time_case1():
    result = obsq.convert_dart_time(0, 0)
    expected = dt.datetime(1601, 1, 1)
    assert result == expected

def test_convert_dart_time_case2():
    result = obsq.convert_dart_time(86400, 0)
    expected = dt.datetime(1601, 1, 2)
    assert result == expected

def test_convert_dart_time_case3():
    result = obsq.convert_dart_time(0, 1)
    expected = dt.datetime(1601, 1, 2)
    assert result == expected

def test_convert_dart_time_case4():
    result = obsq.convert_dart_time(2164, 151240)
    expected = dt.datetime(2015, 1, 31, 0, 36, 4)
    assert result == expected

def test_synonyms_missing_key():
    filename = "obs_seq.final.ascii.syn"
    with pytest.raises(KeyError, match="'observation'"):
        obj3 = obsq.obs_sequence(filename)

def test_synonyms_single():
    filename = "obs_seq.final.ascii.syn"
    obj1 = obsq.obs_sequence(filename, synonyms="observationx")
    assert "observationx" in obj1.synonyms_for_obs

def test_synonyms_list():
    filename = "obs_seq.final.ascii.syn"
    obj2 = obsq.obs_sequence(filename, synonyms=["synonym1", "synonym2", "observationx"])
    assert "synonym1" in obj2.synonyms_for_obs
    assert "synonym2" in obj2.synonyms_for_obs

def test_synonyms_missing_key_per_instance():
    filename = "obs_seq.final.ascii.syn"
    with pytest.raises(KeyError, match="'observation'"):
        obj3 = obsq.obs_sequence(filename)


if __name__ == '__main__':
    pytest.main()