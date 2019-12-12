#!/usr/bin/env bash
protoc -Isrc --python_out=src --mypy_out=src src/harness/options.proto
protoc -Isrc --python_out=src --mypy_out=src src/harness/postgres.proto
protoc -Isrc --python_out=src --mypy_out=src src/harness/grpc.proto
protoc -Isrc -Iexample --python_out=example --python_grpc_out=example --python_harness_out=example --mypy_out=example example/svc.proto
