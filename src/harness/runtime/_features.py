def enable_metrics():
    from opentelemetry.metrics import set_preferred_meter_implementation
    from opentelemetry.sdk.metrics import Meter
    set_preferred_meter_implementation(lambda _: Meter())


def enable_tracing():
    from opentelemetry.trace import set_preferred_tracer_source_implementation
    from opentelemetry.sdk.trace import TracerSource
    set_preferred_tracer_source_implementation(lambda _: TracerSource())
