"""Heuristic inference of observation units.

Observation sequences do not record the units of the observation value.
``infer_units`` makes a best guess for each observation type from the type
name and the range of the observed values.
"""

import os

import numpy as np
import pandas as pd
import yaml

_DEFAULT_UNITS_FILE = os.path.join(os.path.dirname(__file__), "obs_units.yaml")

# Candidate units whose in-range fractions differ by less than this are
# reported as ambiguous.
_TIE_TOLERANCE = 0.02

_COLUMNS = [
    "type",
    "quantity",
    "unit",
    "confidence",
    "alternatives",
    "n_obs",
    "p01",
    "p50",
    "p99",
]


def _load_rules(units_file=None):
    with open(units_file or _DEFAULT_UNITS_FILE, "r") as f:
        return yaml.safe_load(f)


def _match_quantity(type_name, rules):
    """Return the name of the first quantity whose patterns match, else None."""
    name = str(type_name).upper()
    for quantity, rule in rules.items():
        if not any(p.upper() in name for p in rule.get("patterns", [])):
            continue
        if any(x.upper() in name for x in rule.get("exclude", [])):
            continue
        include = rule.get("include")
        if include and not any(i.upper() in name for i in include):
            continue
        return quantity
    return None


def infer_units(df, units_file=None):
    """
    Guess the unit of the observation values for each observation type.

    For each type, the type name selects a quantity (e.g. ocean temperature)
    from a table of plausible value ranges (``obs_units.yaml``). Each
    candidate unit is scored by the fraction of observations inside its range
    and the best scoring unit is returned. If several candidates score
    (nearly) the same, as for salinity in PSU and g/kg, the first is returned
    and the others are listed in ``alternatives``.

    Args:
        df (pandas.DataFrame): Must have ``type`` and ``observation`` columns,
            e.g. ``ObsSequence.df``. It is not modified.
        units_file (str, optional): Path to an alternative YAML file of
            ranges. Defaults to the one shipped with the package.

    Returns:
        pandas.DataFrame: One row per type with columns ``type``,
        ``quantity``, ``unit`` ("unknown" if it could not be inferred),
        ``confidence`` (fraction of observations inside the chosen unit's
        range), ``alternatives`` (comma separated units that fit equally
        well), ``n_obs``, ``p01``, ``p50`` and ``p99``.
    """
    for col in ("type", "observation"):
        if col not in df.columns:
            raise ValueError(f"df must have a '{col}' column")

    rules = _load_rules(units_file)
    rows = []
    for type_name, group in df.groupby("type", sort=True):
        values = pd.to_numeric(group["observation"], errors="coerce").to_numpy()
        values = values[np.isfinite(values)]
        row = {
            "type": type_name,
            "quantity": None,
            "unit": "unknown",
            "confidence": np.nan,
            "alternatives": "",
            "n_obs": len(values),
            "p01": np.nan,
            "p50": np.nan,
            "p99": np.nan,
        }
        if len(values) > 0:
            row["p01"], row["p50"], row["p99"] = np.percentile(values, [1, 50, 99])

        quantity = _match_quantity(type_name, rules)
        row["quantity"] = quantity
        if quantity is not None and len(values) > 0:
            scores = {
                unit: float(np.mean((values >= lo) & (values <= hi)))
                for unit, (lo, hi) in rules[quantity]["units"].items()
            }
            best = max(scores.values())
            if best > 0:
                fits = [u for u, s in scores.items() if best - s <= _TIE_TOLERANCE]
                row["unit"] = fits[0]
                row["alternatives"] = ", ".join(fits[1:])
                row["confidence"] = best
        rows.append(row)

    return pd.DataFrame(rows, columns=_COLUMNS)
