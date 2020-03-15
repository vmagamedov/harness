Wires
=====

This is the main concept of the Harness Framework. Every service needs
to communicate with the outside world. And every communication type have
to be defined and configured.

Wire Types
~~~~~~~~~~

There are two wire types:

- Input wires: for connecting to other services, e.g. databases
- Output wires: for allowing connections from other services, e.g. web servers

That is why :doc:`runtime` passes input wires as an argument to your ``setup``
function, and receives output wires in return.

Input Wires
~~~~~~~~~~~

Runtime options:

* ``(harness.wire).input.type`` - implementation of a wire

Deploy options:

* ``(harness.wire).input.reach`` - enum with such values:

  - ``LOCALHOST`` - destination is on the same host
  - ``NAMESPACE`` - destination is in the same namespace
  - ``CLUSTER`` - destination is in the same cluster
  - ``EXTERNAL`` - destination is outside our cluster

Example:

.. code-block:: protobuf

  message Configuration {
      harness.postgres.Pool db = 1 [
          (harness.wire).input.type = "harness.wires.asyncpg.PoolWire",
          (harness.wire).input.reach = EXTERNAL
      ];
  }

This input wire connects us to the PostgreSQL server, which is located outside
our cluster.

Output Wires
~~~~~~~~~~~~

Runtime options:

* ``(harness.wire).output.type`` - implementation of a wire

Deploy options:

* ``(harness.wire).output.expose`` - enum with such values:

  - ``PRIVATE`` - wire is accessible only on the same host
  - ``HEADLESS`` - wire is accessible internally, without load-balancing
  - ``INTERNAL`` - wire is accessible internally, with load-balancing
  - ``PUBLIC`` - wire is accessible externally

Example:

.. code-block:: protobuf

  message Configuration {
      harness.http.Server server = 1 [
          (harness.wire).output.type = "harness.wires.aiohttp.web.ServerWire",
          (harness.wire).output.expose = PUBLIC
      ];
  }

This output wire starts a HTTP server, which is publicly accessible to everyone.
