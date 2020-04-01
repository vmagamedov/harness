python3 -m grpc_tools.protoc -I. -I$(harness proto-path) \
        --harness_out=runtime=python:. --python_out=. status.proto
