import logging

from opentelemetry.trace import set_preferred_tracer_implementation
from opentelemetry.sdk.trace import tracer
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
      :config: harness.tracing.Exporter
      :requirements: jaeger-client

    """
    _config: tracing_pb2.Exporter

    def configure(self, value: tracing_pb2.Exporter):
        assert isinstance(value, tracing_pb2.Exporter), type(value)
        self._config = value

    async def __aenter__(self):
        set_preferred_tracer_implementation(lambda _: tracer)
        exporter = JaegerSpanExporter(
            service_name=self._config.service_name,
            agent_host_name=self._config.address.host,
            agent_port=self._config.address.port,
        )
        span_processor = BatchExportSpanProcessor(exporter)
        tracer.add_span_processor(span_processor)
        _log.info('%s started: service_name=%s; addr=%s:%d',
                  self.__class__.__name__, self._config.service_name,
                  self._config.address.host, self._config.address.port)
