import datetime as dt

from pydartdiags.obs_sequence import obs_sequence as obs_seq


def test_convert_dart_time():
    # Test case 1: Convert 0 seconds and 0 days
    result = obs_seq.convert_dart_time(0, 0)
    expected = dt.datetime(1601, 1, 1)
    assert result == expected

    # Test case 2: Convert 86400 seconds (1 day) and 0 days
    result = obs_seq.convert_dart_time(86400, 0)
    expected = dt.datetime(1601, 1, 2)
    assert result == expected

    # Test case 3: Convert 0 seconds and 1 day
    result = obs_seq.convert_dart_time(0, 1)
    expected = dt.datetime(1601, 1, 2)
    assert result == expected

    # Test case 4: Convert 3600 seconds (1 hour) and 1 day
    result = obs_seq.convert_dart_time(2164, 151240)
    expected = dt.datetime(2015, 1, 31, 0, 36, 4)
    assert result == expected

    
if __name__ == '__main__':
    pytest.main()