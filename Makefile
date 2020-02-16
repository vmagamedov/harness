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
	rm -f src/validate/$(GENERATED)

proto: clean
	cd src && $(GEN) harness/wire.proto
	cd src && $(GEN) harness/net.proto
	cd src && $(GEN) harness/logging.proto
	cd src && $(GEN) harness/postgres.proto
	cd src && $(GEN) harness/grpc.proto
	cd src && $(GEN) harness/http.proto
	cd src && $(GEN) harness/redis.proto
	cd src && $(GEN) harness/tracing.proto
	cd src && $(GEN) validate/validate.proto
	cd example/web && $(GEN) --harness_out=runtime=python:. kirk.proto
	cd example/grpc && $(GEN) --python_grpc_out=. --harness_out=runtime=python:. scotty.proto
	cd example/cron && $(GEN) --harness_out=runtime=python:. pulsar.proto
	cd example/complex && $(GEN) --harness_out=runtime=python:. spock/service.proto

release: proto
	./scripts/release_check.sh
	rm -rf harness.egg-info
	python setup.py sdist

reference:
	python3 -m grpc_tools.protoc --plugin=scripts/protoc-gen-reference -Isrc --reference_out=docs \
	  src/harness/net.proto \
	  src/harness/http.proto

docs: reference
	PYTHONPATH=docs sphinx-build docs build

run_web:
	@PYTHONPATH=example/web:example/grpc python example/web/entrypoint.py example/web/kirk.yaml

run_grpc:
	@PYTHONPATH=example/grpc python example/grpc/entrypoint.py example/grpc/scotty.yaml

run_cron:
	@PYTHONPATH=example/cron python example/cron/entrypoint.py example/cron/pulsar.yaml

test-kube:
	harness kube-gen example/web/kirk.proto python example/web/kirk.yaml v1 --namespace=platform --instance=ua --base-domain=example.com | pygmentize -l yaml | less -r

test-plugin:
	python3 -m grpc_tools.protoc -Iexample/web -Isrc --python_out=example/web --harness_out=runtime=python:example/web example/web/kirk.proto
