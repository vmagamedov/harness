import logging

from opentelemetry.trace import get_tracer_provider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.ext.jaeger import JaegerSpanExporter
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

from .... import tracing_pb2
from ...base import Wire


_log = logging.getLogger(__name__)


class JaegerSpanExporterWire(Wire):
    """

    .. wire:: harness.wires.opentelemetry.ext.jaeger.JaegerSpanExporterWire
      :type: input
      :runtime: python
      :config: harness.tracing.Jaeger
      :requirements: opentelemetry-ext-jaeger==0.5b0

    """

    _config: tracing_pb2.Jaeger

    def configure(self, value: tracing_pb2.Jaeger):
        assert isinstance(value, tracing_pb2.Jaeger), type(value)
        self._config = value

    async def __aenter__(self):
        exporter = JaegerSpanExporter(
            service_name=self._config.service_name,
            agent_host_name=self._config.address.host,
            agent_port=self._config.address.port,
        )
        span_processor = BatchExportSpanProcessor(exporter)
        source: TracerProvider = get_tracer_provider()
        source.add_span_processor(span_processor)
        _log.info(
            "%s started: service_name=%s; addr=%s:%d",
            self.__class__.__name__,
            self._config.service_name,
            self._config.address.host,
            self._config.address.port,
        )
