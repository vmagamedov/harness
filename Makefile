__default__:
	@echo "Please specify a target to make"

PROTO_PATH=$(abspath src)
GEN=python3 -m grpc_tools.protoc -I. -I$(PROTO_PATH) --python_out=. --mypy_out=.
GENERATED=*{_pb2.py,_grpc.py,_wires.py,.pyi}

clean:
	rm -f example/grpc/$(GENERATED)
	rm -f example/web/$(GENERATED)
	rm -f example/cron/$(GENERATED)
	rm -f example/complex/spock/$(GENERATED)
	rm -f src/harness/$(GENERATED)

proto: clean
	cd src && $(GEN) harness/wire.proto
	cd src && $(GEN) harness/net.proto
	cd src && $(GEN) harness/logging.proto
	cd src && $(GEN) harness/postgres.proto
	cd src && $(GEN) harness/grpc.proto
	cd src && $(GEN) harness/http.proto
	cd src && $(GEN) harness/redis.proto
	cd src && $(GEN) harness/tracing.proto
	cd example/web && $(GEN) --python_harness_out=. kirk.proto
	cd example/grpc && $(GEN) --python_grpc_out=. --python_harness_out=. scotty.proto
	cd example/cron && $(GEN) --python_harness_out=. pulsar.proto
	cd example/complex && $(GEN) --python_harness_out=. spock/service.proto

release: proto
	./scripts/release_check.sh
	rm -rf harness.egg-info
	python setup.py sdist

run_web:
	@PYTHONPATH=example/web:example/grpc python example/web/entrypoint.py example/web/kirk.yaml

run_grpc:
	@PYTHONPATH=example/grpc python example/grpc/entrypoint.py example/grpc/scotty.yaml

run_cron:
	@PYTHONPATH=example/cron python example/cron/entrypoint.py example/cron/pulsar.yaml

gen_web:
	harness kube-gen example/web/kirk.proto example/web/kirk.yaml example/web/kirk.secret.yaml v1 --namespace=platform --instance=ua | pygmentize -l yaml | less -r
