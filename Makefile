__default__:
	@echo "Please specify a target to make"

PROTO_PATH=$(abspath src)
GEN=python3 -m grpc_tools.protoc -I. -I$(PROTO_PATH) --python_out=. --mypy_out=.
GENERATED=*{_pb2.py,_grpc.py,_wires.py,.pyi}

clean:
	rm -f example/grpc/$(GENERATED)
	rm -f example/web/$(GENERATED)
	rm -f example/sched/$(GENERATED)
	rm -f src/harness/$(GENERATED)

proto: clean
	cd src && $(GEN) harness/wire.proto
	cd src && $(GEN) harness/logging.proto
	cd src && $(GEN) harness/postgres.proto
	cd src && $(GEN) harness/grpc.proto
	cd src && $(GEN) harness/http.proto
	cd src && $(GEN) harness/redis.proto
	cd example/grpc && $(GEN) --python_grpc_out=. --python_harness_out=. svc.proto
	cd example/web && $(GEN) --python_harness_out=. svc.proto
	cd example/sched && $(GEN) --python_harness_out=. svc.proto

release: proto
	./scripts/release_check.sh
	rm -rf harness.egg-info
	python setup.py sdist

run_grpc:
	@PYTHONPATH=example/grpc harness svc example/grpc/svc.yaml

run_web:
	@PYTHONPATH=example/web harness svc example/web/svc.yaml

run_sched:
	@PYTHONPATH=example/sched harness svc example/sched/svc.yaml
