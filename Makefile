.PHONY: docs requirements

__default__:
	@echo "Please specify a target to make"

PROTOC=python3 -m grpc_tools.protoc
CLEAN=*{_pb2.py,_grpc.py,_wires.py,.pyi}

HARNESS_PROTOS=$(wildcard src/harness/*.proto)
WIRE_PROTOS=$(filter-out src/harness/wire.proto, $(HARNESS_PROTOS))

GOOGLE_PATH=$(shell scripts/google-proto-path)
GOOGLE_PROTOS=$(GOOGLE_PATH)/google/protobuf/empty.proto

clean-validate-proto:
	rm -f src/validate/$(CLEAN)

validate-proto: clean-validate-proto
	$(PROTOC) -Isrc --python_out=src --mypy_out=quiet:src src/validate/validate.proto

clean-harness-proto:
	rm -f src/harness/$(CLEAN)

harness-proto: clean-harness-proto
	$(PROTOC) -Isrc --python_out=src --mypy_out=quiet:src $(HARNESS_PROTOS)

clean-examples-proto:
	rm -f examples/{web,grpc,cron,asgi}/$(CLEAN)

examples-proto: clean-examples-proto
	$(PROTOC) -Isrc -Iexamples/web --python_out=examples/web --mypy_out=quiet:examples/web --harness_out=runtime=python:examples/web examples/web/kirk.proto
	$(PROTOC) -Isrc -Iexamples/grpc --python_out=examples/grpc --python_grpc_out=examples/grpc --mypy_out=quiet:examples/grpc --harness_out=runtime=python:examples/grpc examples/grpc/scotty.proto
	$(PROTOC) -Isrc -Iexamples/cron --python_out=examples/cron --mypy_out=quiet:examples/cron --harness_out=runtime=python:examples/cron examples/cron/pulsar.proto
	$(PROTOC) -Isrc -Iexamples/asgi --python_out=examples/asgi --mypy_out=quiet:examples/asgi --harness_out=runtime=python:examples/asgi examples/asgi/mccoy.proto

proto: validate-proto harness-proto examples-proto

release: validate-proto harness-proto
	./scripts/release_check.sh
	rm -rf src/harness.egg-info
	python setup.py sdist

reference:
	python3 -m grpc_tools.protoc --plugin=scripts/protoc-gen-reference --reference_out=docs $(GOOGLE_PATH)/google/protobuf/empty.proto
	python3 -m grpc_tools.protoc --plugin=scripts/protoc-gen-reference -Isrc --reference_out=docs ${WIRE_PROTOS}
	python3 -m grpc_tools.protoc --plugin=scripts/protoc-gen-typeinfo --typeinfo_out=docs/_static -Isrc ${WIRE_PROTOS}

docs:
	PYTHONPATH=docs sphinx-build docs build

requirements:
	pip-compile --output-file=requirements/setup.txt setup.py
	pip-compile requirements/check.in
	pip-compile requirements/docs.in
	pip-compile requirements/release.in
	pip-compile requirements/test.in

run_web:
	@PYTHONPATH=examples/web:examples/grpc python examples/web/entrypoint.py examples/web/kirk.yaml

run_grpc:
	@PYTHONPATH=examples/grpc python examples/grpc/entrypoint.py examples/grpc/scotty.yaml

run_cron:
	@PYTHONPATH=examples/cron python examples/cron/entrypoint.py examples/cron/pulsar.yaml

run_asgi:
	@PYTHONPATH=examples/asgi python examples/asgi/entrypoint.py examples/asgi/mccoy.yaml

test-kube:
	harness kube-gen python examples/web/kirk.proto examples/web/kirk.yaml v1 --namespace=platform --instance=ua --base-domain=example.com | pygmentize -l yaml | less -r

test-check:
	harness check examples/web/kirk.proto examples/web/kirk.yaml
