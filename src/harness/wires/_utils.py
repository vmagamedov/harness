import ipaddress
from http import HTTPStatus
from typing import Dict

from opentelemetry.trace.status import StatusCanonicalCode


HTTP_STATUS_TO_CODE_MAP: Dict[int, StatusCanonicalCode] = {
    # 401
    HTTPStatus.UNAUTHORIZED.value: StatusCanonicalCode.UNAUTHENTICATED,
    # 403
    HTTPStatus.FORBIDDEN.value: StatusCanonicalCode.PERMISSION_DENIED,
    # 404
    HTTPStatus.NOT_FOUND.value: StatusCanonicalCode.NOT_FOUND,
    # 429
    HTTPStatus.TOO_MANY_REQUESTS.value: StatusCanonicalCode.RESOURCE_EXHAUSTED,
    # 501
    HTTPStatus.NOT_IMPLEMENTED.value: StatusCanonicalCode.UNIMPLEMENTED,
    # 503
    HTTPStatus.SERVICE_UNAVAILABLE.value: StatusCanonicalCode.UNAVAILABLE,
    # 504
    HTTPStatus.GATEWAY_TIMEOUT.value: StatusCanonicalCode.DEADLINE_EXCEEDED,
}


def status_to_canonical_code(status_code: int) -> StatusCanonicalCode:
    try:
        return HTTP_STATUS_TO_CODE_MAP[status_code]
    except KeyError:
        if status_code < 100:
            return StatusCanonicalCode.UNKNOWN
        elif status_code < 400:
            return StatusCanonicalCode.OK
        elif status_code < 500:
            return StatusCanonicalCode.INVALID_ARGUMENT
        elif status_code < 600:
            return StatusCanonicalCode.INTERNAL
        else:
            return StatusCanonicalCode.UNKNOWN


def is_internal_request(host: str) -> bool:
    address, _, _ = host.partition(":")
    try:
        ipaddress.ip_address(address)
    except ValueError:
        return address == "localhost"
    else:
        return True
