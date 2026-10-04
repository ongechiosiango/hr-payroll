"""Tests for the CSV register."""

import pytest

from hr_payroll.config import Bracket, TaxConfig
from hr_payroll.register import RegisterError, load_employees, process_register


def _config():
    return TaxConfig(
        currency="USD",
        brackets=[Bracket(up_to=None, rate=0.10)],
        social_security_rate=0,
        medicare_rate=0,
        pension_rate=0,
    )


def _write(tmp_path, text):
    p = tmp_path / "employees.csv"
    p.write_text(text)
    return str(p)


def test_load_employees_ok(tmp_path):
    path = _write(tmp_path, "name,gross\nAlice,50000\nBob,60000\n")
    rows = load_employees(path)
    assert len(rows) == 2
    assert rows[0]["name"] == "Alice"


def test_load_employees_missing_file(tmp_path):
    with pytest.raises(RegisterError, match="not found"):
        load_employees(str(tmp_path / "nope.csv"))


def test_load_employees_missing_columns(tmp_path):
    path = _write(tmp_path, "foo,bar\n1,2\n")
    with pytest.raises(RegisterError, match="missing required column"):
        load_employees(path)


def test_process_register_computes_for_each(tmp_path):
    path = _write(tmp_path, "name,gross\nAlice,50000\nBob,10000\n")
    rows = process_register(path, _config())
    assert len(rows) == 2
    assert rows[0].name == "Alice"
    assert rows[0].result.net < rows[0].result.gross
    assert rows[1].name == "Bob"


def test_process_register_bad_gross(tmp_path):
    path = _write(tmp_path, "name,gross\nAlice,abc\n")
    with pytest.raises(RegisterError, match="invalid gross"):
        process_register(path, _config())


def test_process_register_missing_name(tmp_path):
    path = _write(tmp_path, "name,gross\n,50000\n")
    with pytest.raises(RegisterError, match="missing 'name'"):
        process_register(path, _config())
