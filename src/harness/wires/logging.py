import logging

from .. import logging_pb2

from .base import Wire


_LEVELS_MAP = {
    logging_pb2.Level.NOTSET: logging.NOTSET,
    logging_pb2.Level.DEBUG: logging.DEBUG,
    logging_pb2.Level.INFO: logging.INFO,
    logging_pb2.Level.WARNING: logging.WARNING,
    logging_pb2.Level.CRITICAL: logging.CRITICAL,
}


class ConsoleWire(Wire):
    handler = None

    def configure(self, value: logging_pb2.Console):
        from metricslog.ext.formatter import ColorFormatter

        logging.captureWarnings(True)
        self.handler = logging.StreamHandler()
        self.handler.setFormatter(ColorFormatter())
        logging.root.addHandler(self.handler)

        level = _LEVELS_MAP[value.level]
        if level is not logging.NOTSET:
            if logging.root.level is not logging.NOTSET:
                level = min(level, logging.root.level)
            logging.root.setLevel(level)


class SyslogWire(Wire):
    pass
