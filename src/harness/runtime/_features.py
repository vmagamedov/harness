def enable_metrics() -> None:
    from opentelemetry.metrics import set_meter_provider
    from opentelemetry.sdk.metrics import MeterProvider

    set_meter_provider(MeterProvider())


def enable_tracing() -> None:
    from opentelemetry.trace import set_tracer_provider
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.trace.sampling import DEFAULT_OFF

    set_tracer_provider(TracerProvider(sampler=DEFAULT_OFF))
