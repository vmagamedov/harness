def enable_metrics():
    from opentelemetry.metrics import set_meter_provider
    from opentelemetry.sdk.metrics import MeterProvider

    set_meter_provider(MeterProvider())


def enable_tracing():
    from opentelemetry.trace import set_tracer_provider
    from opentelemetry.sdk.trace import TracerProvider

    set_tracer_provider(TracerProvider())
