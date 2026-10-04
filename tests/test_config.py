"""Tests for the tax config loader."""

import json
from decimal import Decimal

import pytest

from hr_payroll.config import ConfigError, load_config


def _write(tmp_path, data):
    p = tmp_path / "taxes.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_load_minimal(tmp_path):
    path = _write(tmp_path, {"currency": "USD"})
    cfg = load_config(path)
    assert cfg.currency == "USD"
    assert cfg.brackets == []


def test_load_with_brackets(tmp_path):
    path = _write(tmp_path, {
        "income_tax_brackets": [
            {"up_to": 10000, "rate": 0.0},
            {"up_to": None, "rate": 0.25},
        ],
    })
    cfg = load_config(path)
    assert len(cfg.brackets) == 2
    assert cfg.brackets[0].up_to == 10000
    assert cfg.brackets[1].up_to is None
    assert cfg.brackets[1].rate == 0.25


def test_load_missing_file(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(str(tmp_path / "nope.json"))


def test_load_invalid_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not json")
    with pytest.raises(ConfigError, match="Invalid JSON"):
        load_config(str(p))


def test_bracket_rate_out_of_range(tmp_path):
    path = _write(tmp_path, {
        "income_tax_brackets": [{"up_to": 1000, "rate": 1.5}],
    })
    with pytest.raises(ConfigError, match="between 0 and 1"):
        load_config(path)


def test_bracket_missing_rate(tmp_path):
    path = _write(tmp_path, {
        "income_tax_brackets": [{"up_to": 1000}],
    })
    with pytest.raises(ConfigError, match="rate"):
        load_config(path)


def test_social_security_cap_optional(tmp_path):
    path = _write(tmp_path, {"social_security_rate": 0.06})
    cfg = load_config(path)
    assert cfg.social_security_rate == Decimal("0.06")
    assert cfg.social_security_cap is None
