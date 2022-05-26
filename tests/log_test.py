from bole.log import create_logger, log


def test_core_log():
    log.info("VALIDATED")


def test_create_log():
    create_logger("dummy", log_level="INFO").info("VALIDATED")
