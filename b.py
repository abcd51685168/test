import logging
import logging.handlers

log = logging.getLogger("b")
log.info("b")


def bb():
    log.info("BB")
