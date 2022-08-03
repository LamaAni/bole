from bole.log.commands import create_logger   # noqa F401
from bole.log.formatter import BoleLogFormatter   # noqa F401
from bole.log.logger import BoleLogger  # noqa F401

log = create_logger("bole-log-core")

if __name__ == "__main__":
    formatter = BoleLogFormatter()
    try:
        raise Exception("Test")
    except Exception as ex:
        log.error("Test catch", exc_info=ex)

    print(formatter.format_log_message("lasd"))
    log.debug("aadsad")
    log.critical("asd")
    log.warning("Lama")
    log.error("asdsad")
    log.info("Test ")
