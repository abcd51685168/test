import logging
import logging.handlers
from b import bb

log = logging.getLogger()


def init_logging():
    formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    fh = logging.handlers.WatchedFileHandler("/tmp/test.log")
    fh.setFormatter(formatter)
    log.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    log.addHandler(ch)

    log.setLevel(logging.INFO)

if __name__ == "__main__":
    init_logging()
    log.info("a")
    bb()
