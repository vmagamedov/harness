__default__:
	@echo "Please specify a target to make"

PROTO_PATH=$(abspath src)
GEN=protoc -I. -I$(PROTO_PATH) --python_out=. --mypy_out=.
GENERATED=*{_pb2.py,_grpc.py,_wires.py,.pyi}

clean:
	rm -f example/$(GENERATED)
	rm -f src/harness/$(GENERATED)

proto: clean
	cd src && $(GEN) harness/options.proto
	cd src && $(GEN) harness/postgres.proto
	cd src && $(GEN) harness/grpc.proto
	cd example && $(GEN) --python_grpc_out=. --python_harness_out=. svc.proto

release: proto
	./scripts/release_check.sh
	rm -rf harness.egg-info
	python setup.py sdist

run:
	@PYTHONPATH=example harness svc example/config.yaml
