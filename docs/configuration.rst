Configuration
=============

Harness uses `Protocol Buffers`_ as a language-neutral and extensible interface
definition language to define configuration.

Example:

.. code-block:: protobuf

  syntax = "proto3";

  package example;

  import "harness/wire.proto";
  import "harness/http.proto";
  import "harness/postgres.proto";

  message Configuration {
      option (harness.service).name = "example";

      bool debug = 1;

      harness.postgres.Pool db = 2 [
          (harness.wire).input = "python/asyncpg:PoolWire"
      ];
      harness.http.Server server = 3 [
          (harness.wire).output = "python/aiohttp:ServerWire"
      ];
  }

.. _Protocol Buffers: https://developers.google.com/protocol-buffers
