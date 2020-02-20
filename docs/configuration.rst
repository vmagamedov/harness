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

.. note:: It is required that your message type was named ``Configuration``,
  this is a convention over configuration.

This example probably differs from what you expected to see in a ``.proto``
files because we are using message and field options:

- ``(harness.service).name`` - message option to provide service's name
- ``(harness.wire).input`` - field option to describe a wire

These options are defined in the :doc:`harness/wire.proto` file
and it is required to import this file in order to use them.

Wires Definition
~~~~~~~~~~~~~~~~

You can plug wires into your service by describing them in your configuration.
Wire definition look like this:

.. code-block:: text

  harness.http.Server server = 3 [(harness.wire).output = "..."];
  ^-----------------^             ^---------------------------^
  wire's configuration               wire's type and options

Where:

- :proto:message:`harness.http.Server` - is a runtime configuration format
  of a wire
- ``(harness.wire).output = "..."`` - is a compile-time configuration of a wire,
  it describes which wire implementation you wish to use and other options

Runtime Configuration
~~~~~~~~~~~~~~~~~~~~~

`Protocol Buffers`_ has a canonical encoding into JSON, and YAML is chosen as a
more human-friendly format. So even if your configuration is described as a
protobuf message, this doesn't mean that you have to deal with a binary data.
Your runtime configuration is provided via YAML files.

Here is an example of a :proto:message:`harness.http.Server` configuration:

.. code-block:: yaml

  server:              # name of a wire in your Configuration
    bind:              # value for a harness.http.Server message type
      host: 0.0.0.0
      port: 8000

Validation
~~~~~~~~~~

`Protocol Buffers`_ format provides a solid type system to describe your data,
but it doesn't include any of validation facilities. For a data validation
we are using protoc-gen-validate_ project:

.. code-block:: protobuf

  import "validate/validate.proto";

  message Configuration {
      string support_email = 1 [(validate.rules).string.email = true];
  }

This validation also works across different programming languages.

Harness validates your configuration when your service starts and before your
service deploys. You can even validate your configurations without starting your
services as an additional step in your CI/CD pipeline or using a pre-commit
hooks.

.. code-block:: console

  $ harness check service.proto service.yaml
  Validation error: host length is less than 1

Secrets
~~~~~~~

You can provide secrets for your service using `JSON Merge Patch`_ or
`JSON Patch`_ formats. Secrets are applied to the main
configuration and then validated as described in the previous section.

Here is how a connection to the database can be configured in a public
configuration:

.. code-block:: yaml

  db:
    address:
      host: postgres.acme.svc.cluster.local
      port: 5432
    username: concierge
    database: users

Here is how a secrets merge patch looks like:

.. code-block:: yaml

  db:
    password: "really-strong-secret"

.. _Protocol Buffers: https://developers.google.com/protocol-buffers
.. _protoc-gen-validate: https://github.com/envoyproxy/protoc-gen-validate
.. _JSON Merge Patch: https://tools.ietf.org/html/rfc7386
.. _JSON Patch: https://tools.ietf.org/html/rfc6902
