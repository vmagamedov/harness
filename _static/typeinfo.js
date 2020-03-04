const Protocol = {
  TCP: 'tcp',
  HTTP: 'http',
  GRPC: 'grpc',
};

export const TypeInfo = {
  "harness.net.Address": Protocol.TCP,
  "harness.net.Server": Protocol.TCP,
  "harness.postgres.Pool": Protocol.TCP,
  "harness.metrics.Prometheus": Protocol.HTTP,
  "harness.grpc.Channel": Protocol.GRPC,
  "harness.grpc.Server": Protocol.GRPC,
  "harness.redis.Connection": Protocol.TCP,
  "harness.tracing.Jaeger": Protocol.TCP,
  "harness.http.Connection": Protocol.HTTP,
  "harness.http.Server": Protocol.HTTP,
};
