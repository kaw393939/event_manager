import pytest
from app.utils import common
import os
import tempfile
import logging.config

def test_is_empty():
    assert common.is_empty("")
    assert common.is_empty([])
    assert not common.is_empty("hello")
    assert not common.is_empty([1,2])
    assert common.is_empty(None)


def test_safe_get():
    d = {"a": 1, "b": 2}
    assert common.safe_get(d, "a") == 1
    assert common.safe_get(d, "z") is None
    assert common.safe_get(d, "z", default=5) == 5
    assert common.safe_get([1,2], "a", default=7) == 7


def test_setup_logging_success(monkeypatch, tmp_path):
    # Create a minimal logging.conf
    conf_path = tmp_path / "logging.conf"
    conf_path.write_text("""
[loggers]
keys=root
[handlers]
keys=consoleHandler
[formatters]
keys=simpleFormatter
[logger_root]
level=DEBUG
handlers=consoleHandler
[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=simpleFormatter
args=(sys.stdout,)
[formatter_simpleFormatter]
format=%(asctime)s - %(levelname)s - %(message)s
""")
    # Patch __file__ to simulate location
    monkeypatch.setattr(common, "__file__", str(tmp_path / "fake_common.py"))
    monkeypatch.setattr(os.path, "dirname", lambda x: str(tmp_path))
    monkeypatch.setattr(logging.config, "fileConfig", lambda path, disable_existing_loggers: True)
    # Should not raise
    common.setup_logging()


def test_setup_logging_file_not_found(monkeypatch, tmp_path):
    # Patch __file__ to simulate location
    monkeypatch.setattr(common, "__file__", str(tmp_path / "fake_common.py"))
    monkeypatch.setattr(os.path, "dirname", lambda x: str(tmp_path))
    # Remove fileConfig so it tries to open the file
    monkeypatch.setattr(logging.config, "fileConfig", logging.config.fileConfig)
    # Should raise FileNotFoundError
    with pytest.raises(Exception):
        common.setup_logging()

# Add more tests as needed for uncovered functions in common.py
