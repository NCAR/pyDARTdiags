import numpy as np
import pandas as pd
import pytest

from pydartdiags.obs_sequence.units import infer_units


def _df(**types):
    rows = [(t, v) for t, vals in types.items() for v in vals]
    return pd.DataFrame(rows, columns=["type", "observation"])


def _row(result, t):
    return result[result["type"] == t].iloc[0]


class TestInferUnits:
    def test_ocean_temperature_degC(self):
        r = infer_units(_df(CTD_TEMPERATURE=[2.0, 10.5, 18.0, 25.0]))
        row = _row(r, "CTD_TEMPERATURE")
        assert row["unit"] == "degC"
        assert row["quantity"] == "ocean_temperature"
        assert row["confidence"] == 1.0

    def test_ocean_temperature_kelvin(self):
        r = infer_units(_df(XBT_TEMPERATURE=[275.0, 285.0, 295.0]))
        assert _row(r, "XBT_TEMPERATURE")["unit"] == "K"

    def test_atmospheric_temperature_kelvin(self):
        r = infer_units(_df(ACARS_TEMPERATURE=[220.0, 250.0, 290.0]))
        row = _row(r, "ACARS_TEMPERATURE")
        assert row["unit"] == "K"
        assert row["quantity"] == "atmos_temperature"

    def test_salinity_is_ambiguous(self):
        r = infer_units(_df(CTD_SALINITY=[33.0, 34.5, 35.2]))
        row = _row(r, "CTD_SALINITY")
        assert row["unit"] == "PSU"
        assert "g/kg" in row["alternatives"]

    def test_pressure_units(self):
        r = infer_units(_df(A_PRESSURE=[90000.0, 100000.0], B_PRESSURE=[900.0, 1010.0]))
        assert _row(r, "A_PRESSURE")["unit"] == "Pa"
        assert _row(r, "B_PRESSURE")["unit"] == "hPa"

    def test_unknown_type(self):
        r = infer_units(_df(FOO_BAR=[1.0, 2.0]))
        row = _row(r, "FOO_BAR")
        assert row["unit"] == "unknown"
        assert row["quantity"] is None

    def test_out_of_range_is_unknown(self):
        r = infer_units(_df(CTD_TEMPERATURE=[5000.0, 6000.0]))
        assert _row(r, "CTD_TEMPERATURE")["unit"] == "unknown"

    def test_nan_ignored_and_all_nan(self):
        r = infer_units(
            _df(CTD_TEMPERATURE=[10.0, np.nan, 12.0], XBT_TEMPERATURE=[np.nan])
        )
        assert _row(r, "CTD_TEMPERATURE")["n_obs"] == 2
        assert _row(r, "CTD_TEMPERATURE")["unit"] == "degC"
        assert _row(r, "XBT_TEMPERATURE")["unit"] == "unknown"

    def test_mixed_units_lower_confidence(self):
        r = infer_units(_df(CTD_TEMPERATURE=[10.0, 12.0, 14.0, 290.0]))
        row = _row(r, "CTD_TEMPERATURE")
        assert row["unit"] == "degC"
        assert row["confidence"] == pytest.approx(0.75)

    def test_does_not_modify_input(self):
        df = _df(CTD_TEMPERATURE=[10.0, 12.0])
        before = df.copy()
        infer_units(df)
        pd.testing.assert_frame_equal(df, before)

    def test_missing_column(self):
        with pytest.raises(ValueError):
            infer_units(pd.DataFrame({"type": ["A"]}))
