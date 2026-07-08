import os
import logging
import pytest
from app.utils.common import setup_logging

def test_setup_logging(tmp_path):
    # Create a temporary logging.conf file
    logging_conf = tmp_path / "logging.conf"
    logging_conf.write_text("""
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
formatter=simpleFormatter
args=(sys.stdout,)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
    """)
    
    # Patch the path to use our temporary file
    with pytest.MonkeyPatch().context() as m:
        m.setattr("os.path.normpath", lambda x: str(logging_conf))
        setup_logging()
        
    # Verify logger was configured
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) > 0