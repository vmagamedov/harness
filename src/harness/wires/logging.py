import sys
import json
import logging.handlers

from .. import logging_pb2

from .base import Wire


if hasattr(sys.stderr, "isatty") and sys.stderr.isatty():
    try:
        import pygments  # noqa
    except ImportError:
        _WITH_COLORS = False
    else:
        from pygments import highlight
        from pygments.console import ansiformat
        from pygments.lexers.python import PythonTracebackLexer
        from pygments.formatters.terminal import TerminalFormatter

        _WITH_COLORS = True
else:
    _WITH_COLORS = False


_LEVELS_MAP = {
    logging_pb2.Level.NOTSET: logging.NOTSET,
    logging_pb2.Level.DEBUG: logging.DEBUG,
    logging_pb2.Level.INFO: logging.INFO,
    logging_pb2.Level.WARNING: logging.WARNING,
    logging_pb2.Level.ERROR: logging.ERROR,
    logging_pb2.Level.CRITICAL: logging.CRITICAL,
}

_LEVEL_COLORS = {
    logging.DEBUG: "brightblack",
    logging.INFO: "green",
    logging.WARNING: "yellow",
    logging.ERROR: "red",
    logging.CRITICAL: "*red*",
}

_TEXT_COLORS = {
    logging.DEBUG: "brightblack",
    logging.INFO: "",
    logging.WARNING: "",
    logging.ERROR: "",
    logging.CRITICAL: "",
}


def _wrap_text(level: int, value: str):
    return ansiformat(_TEXT_COLORS[level], value)


def _wrap_level(level, value: str):
    return ansiformat(_LEVEL_COLORS[level], value)


def _highlight(text):
    return highlight(text, lexer=PythonTracebackLexer(), formatter=TerminalFormatter())


_FMT = "{asctime} {levelname} {name} {message}"


class _ColorFormatter(logging.Formatter):
    def format(self, record):
        record.asctime = self.formatTime(record)
        record.message = record.getMessage()
        message = _FMT.format(
            asctime=_wrap_text(record.levelno, record.asctime),
            levelname=_wrap_level(record.levelno, record.levelname),
            name=_wrap_text(record.levelno, record.name),
            message=_wrap_text(record.levelno, record.message),
        )
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            if _WITH_COLORS:
                exc_text = _highlight(exc_text).rstrip("\n")
            message += "\n" + exc_text
        return message


class ConsoleWire(Wire):
    """

    .. wire:: harness.wires.logging.ConsoleWire
      :type: input
      :runtime: python
      :config: harness.logging.Console
      :requirements: pygments

    """

    _handler: logging.Handler

    def configure(self, value: logging_pb2.Console):
        logging.captureWarnings(True)

        self._handler = logging.StreamHandler()

        if _WITH_COLORS:
            self._handler.setFormatter(_ColorFormatter())
        else:
            self._handler.setFormatter(logging.Formatter(fmt=_FMT, style="{"))

        level = _LEVELS_MAP[value.level]
        self._handler.setLevel(level)

        logging.root.addHandler(self._handler)
        if level is not logging.NOTSET:
            if logging.root.level is not logging.NOTSET:
                level = min(level, logging.root.level)
            logging.root.setLevel(level)


class _CEEFormatter(logging.Formatter):
    def format(self, record):
        message = record.getMessage()
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            if _WITH_COLORS:
                exc_text = _highlight(exc_text).rstrip("\n")
            message += "\n" + exc_text
        value = json.dumps({"logger": record.name, "message": message})
        return "@cee: {}".format(value)


class _SyslogHandler(logging.handlers.SysLogHandler):
    def __init__(self, *args, app_name, **kwargs):
        super().__init__(*args, **kwargs)
        self.ident = f"{app_name}: "


_FACILITY_MAP = {
    logging_pb2.Syslog.NOTSET: logging.handlers.SysLogHandler.LOG_USER,
    logging_pb2.Syslog.USER: logging.handlers.SysLogHandler.LOG_USER,
    logging_pb2.Syslog.LOCAL0: logging.handlers.SysLogHandler.LOG_LOCAL0,
    logging_pb2.Syslog.LOCAL1: logging.handlers.SysLogHandler.LOG_LOCAL1,
    logging_pb2.Syslog.LOCAL2: logging.handlers.SysLogHandler.LOG_LOCAL2,
    logging_pb2.Syslog.LOCAL3: logging.handlers.SysLogHandler.LOG_LOCAL3,
    logging_pb2.Syslog.LOCAL4: logging.handlers.SysLogHandler.LOG_LOCAL4,
    logging_pb2.Syslog.LOCAL5: logging.handlers.SysLogHandler.LOG_LOCAL5,
    logging_pb2.Syslog.LOCAL6: logging.handlers.SysLogHandler.LOG_LOCAL6,
    logging_pb2.Syslog.LOCAL7: logging.handlers.SysLogHandler.LOG_LOCAL7,
}


class SyslogWire(Wire):
    """

    .. wire:: harness.wires.logging.SyslogWire
      :type: input
      :runtime: python
      :config: harness.logging.Syslog
      :requirements:

    """

    _handler: logging

    def configure(self, value: logging_pb2.Syslog):
        logging.captureWarnings(True)

        self._handler = _SyslogHandler(
            app_name=value.app,
            address="/dev/log",
            facility=_FACILITY_MAP[value.facility],
        )
        self._handler.setFormatter(_CEEFormatter())

        level = _LEVELS_MAP[value.level]
        self._handler.setLevel(level)

        logging.root.addHandler(self._handler)
        if level is not logging.NOTSET:
            if logging.root.level is not logging.NOTSET:
                level = min(level, logging.root.level)
            logging.root.setLevel(level)
