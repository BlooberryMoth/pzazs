import logging, sys


class CustomLoggingFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style="%", validate=True, *, defaults=None):
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

    FORMATS = {
        logging.DEBUG: "\x1b[1;30m%(asctime)s \x1b[1;34m%(levelname)s    \x1b[1;36m%(name)s \x1b[m%(message)s",
        logging.INFO: "\x1b[1;30m%(asctime)s \x1b[1;34m%(levelname)s     \x1b[1;36m%(name)s \x1b[m%(message)s",
        logging.WARNING: "\x1b[1;30m%(asctime)s \x1b[1;33m%(levelname)s  \x1b[1;36m%(name)s \x1b[m%(message)s",
        logging.ERROR: "\x1b[1;30m%(asctime)s \x1b[1;31m%(levelname)s    \x1b[1;36m%(name)s \x1b[m%(message)s",
        logging.CRITICAL: "\x1b[1;30m%(asctime)s \x1b[1;41m%(levelname)s\x1b[m\x1b[1;36m %(name)s \x1b[m%(message)s",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
        return formatter.format(record)


LOG = logging.getLogger("PZ(az)S")
LOG.setLevel(logging.INFO)
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setFormatter(CustomLoggingFormatter(datefmt="%Y-%m-%d %H:%M:%S"))
LOG.addHandler(log_handler)