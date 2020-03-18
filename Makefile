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

clean-example-proto:
	rm -f example/{web,grpc,cron}/$(CLEAN)

example-proto: clean-example-proto
	$(PROTOC) -Isrc -Iexample/web --python_out=example/web --mypy_out=quiet:example/web --harness_out=runtime=python:example/web example/web/kirk.proto
	$(PROTOC) -Isrc -Iexample/grpc --python_out=example/grpc --python_grpc_out=example/grpc --mypy_out=quiet:example/grpc --harness_out=runtime=python:example/grpc example/grpc/scotty.proto
	$(PROTOC) -Isrc -Iexample/cron --python_out=example/cron --mypy_out=quiet:example/cron --harness_out=runtime=python:example/cron example/cron/pulsar.proto

proto: validate-proto harness-proto example-proto

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
	@PYTHONPATH=example/web:example/grpc python example/web/entrypoint.py example/web/kirk.yaml

run_grpc:
	@PYTHONPATH=example/grpc python example/grpc/entrypoint.py example/grpc/scotty.yaml

run_cron:
	@PYTHONPATH=example/cron python example/cron/entrypoint.py example/cron/pulsar.yaml

test-kube:
	harness kube-gen python example/web/kirk.proto example/web/kirk.yaml v1 --namespace=platform --instance=ua --base-domain=example.com | pygmentize -l yaml | less -r

test-check:
	harness check example/web/kirk.proto example/web/kirk.yaml
