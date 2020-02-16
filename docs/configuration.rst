Configuration
=============

Harness uses `Protocol Buffers`_ as a language-neutral and extensible interface
definition language to define a configuration. Such configuration looks like
this:

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
          (harness.wire).input = "harness.wires.asyncpg.PoolWire"
      ];
      harness.http.Server server = 3 [
          (harness.wire).output = "harness.wires.aiohttp.web.ServerWire"
      ];
  }

This example probably differs from what you expected to see in a ``.proto``
files because we are using message and field options:

- ``(harness.service).name`` - message option to provide service's name
- ``(harness.wire).input`` - field option to describe a wire

These options are defined in the ``harness/wire.proto`` file and it is required
to import this file in order to use them.

Wires
~~~~~

You can plug wires into your service by describing them in your configuration:

.. code-block:: text

  harness.http.Server server = 3 [(harness.wire).output = "..."]
  ^^^^^^^^^^^^^^^^^^^             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  |                               |
  ` wire's configuration format   ` wire type and other options

YAML
~~~~


Validation
~~~~~~~~~~


Secrets
~~~~~~~


.. _Protocol Buffers: https://developers.google.com/protocol-buffers
