from opentelemetry.trace import set_preferred_tracer_implementation
from opentelemetry.sdk.trace import tracer
from opentelemetry.ext.jaeger import JaegerSpanExporter
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

from .... import tracing_pb2

from ...base import Wire


class JaegerSpanExporterWire(Wire):

    def configure(self, value: tracing_pb2.Exporter):
        assert isinstance(value, tracing_pb2.Exporter), type(value)

        set_preferred_tracer_implementation(lambda _: tracer)
        exporter = JaegerSpanExporter(
            service_name=value.service_name,
            agent_host_name=value.address.host,
            agent_port=value.address.port,
        )
        span_processor = BatchExportSpanProcessor(exporter)
        tracer.add_span_processor(span_processor)
        print(
            f'Configured {exporter.__class__.__name__};'
            f' service_name={exporter.service_name}'
            f' host={exporter.agent_host_name}'
            f' port={exporter.agent_port}'
        )
