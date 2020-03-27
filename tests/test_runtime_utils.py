from typing import List, Dict

from opentelemetry.correlationcontext import get_correlation

from harness.runtime._utils import CorrelationContextPropagatorWithRequestID


def _getter(carrier: Dict[str, str], header_name: str) -> List[str]:
    return [carrier[header_name]] if header_name in carrier else []


def test_extract():
    propagator = CorrelationContextPropagatorWithRequestID()
    carrier = {"x-request-id": "42"}
    context = propagator.extract(_getter, carrier)
    assert get_correlation("requestId", context) == "42"
