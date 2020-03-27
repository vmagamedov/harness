def enable_request_id():
    from opentelemetry.propagators import set_global_httptextformat
    from opentelemetry.propagators.composite import CompositeHTTPPropagator
    from opentelemetry.trace.propagation.tracecontexthttptextformat import (
        TraceContextHTTPTextFormat,
    )

    from ._utils import CorrelationContextPropagatorWithRequestID

    set_global_httptextformat(
        CompositeHTTPPropagator(
            [TraceContextHTTPTextFormat(), CorrelationContextPropagatorWithRequestID()]
        )
    )


def enable_metrics():
    from opentelemetry.metrics import set_meter_provider
    from opentelemetry.sdk.metrics import MeterProvider

    set_meter_provider(MeterProvider())


def enable_tracing():
    from opentelemetry.trace import set_tracer_provider
    from opentelemetry.sdk.trace import TracerProvider

    set_tracer_provider(TracerProvider())
