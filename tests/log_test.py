from bole.log import create_logger, log


def test_core_log():
    log.info("VALIDATED")


def test_create_log():
    create_logger("dummy", log_level="INFO").info("VALIDATED")


def test_log_with_exception():
    try:
        raise Exception("Test exception")
    except Exception as ex:
        log.error("Test exception", exc_info=ex)


def test_log_with_untyped_exception():
    try:
        # Should not print the exception, but should not fail.
        raise "Test exception"
    except Exception as ex:
        log.error("Test exception", exc_info=ex)
