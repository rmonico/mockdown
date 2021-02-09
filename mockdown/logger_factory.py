import logging
import sys


_to_logging_verbosity_level = {
    (0, "NOTSET"): logging.NOTSET,
    (1, "CRITICAL"): logging.CRITICAL,
    (2, "ERROR"): logging.ERROR,
    (3, "WARNING"): logging.WARNING,
    (4, "INFO"): logging.INFO,
    (5, "DEBUG"): logging.DEBUG,
}

def make_verbosity_argument(parser):
    # TODO Limit choices
    return parser.add_argument('--verbosity', '-v', action='count', default=0, help='Verbosity level')

def get_log_level(verbosity):
    for key, level in _to_logging_verbosity_level.items():
        if verbosity in key:
            return level

    return None

def create(name, verbosity=None, log_level=0):
    logging.basicConfig()
    logger = logging.getLogger(name)

    level = get_log_level(verbosity) if verbosity else log_level

    logger.setLevel(level)

    return logger

