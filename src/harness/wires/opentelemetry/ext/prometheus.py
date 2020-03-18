import logging

from prometheus_client import start_http_server

from opentelemetry import metrics
from opentelemetry.ext.prometheus import PrometheusMetricsExporter
from opentelemetry.sdk.metrics.export.controller import PushController

from .... import metrics_pb2
from ...base import Wire, WaitMixin


_log = logging.getLogger(__name__)


class PrometheusMetricsExporterWire(WaitMixin, Wire):
    """

    .. wire:: harness.wires.opentelemetry.ext.prometheus.PrometheusMetricsExporterWire
      :type: output
      :runtime: python
      :config: harness.metrics.Prometheus
      :requirements: opentelemetry-ext-prometheus==0.5b0

    """

    _config: metrics_pb2.Prometheus
    _controller: PushController

    def configure(self, value: metrics_pb2.Prometheus):
        assert isinstance(value, metrics_pb2.Prometheus), type(value)
        self._config = value

    async def __aenter__(self):
        meter = metrics.get_meter(__name__)
        exporter = PrometheusMetricsExporter(self._config.prefix)
        self._controller = PushController(meter, exporter, 5)

        start_http_server(self._config.bind.port, self._config.bind.host)
        _log.info(
            "%s started: addr=%s:%d",
            self.__class__.__name__,
            self._config.bind.host,
            self._config.bind.port,
        )

    def close(self):
        super().close()
        if not self._controller.finished.is_set():
            self._controller.shutdown()
