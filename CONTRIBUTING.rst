Here is how to distribute new Wires
===================================

Harness uses entry points feature of pkg_resources_, as a way to discover
installed wires.

These entry points are defined in a ``setup.py`` script under an
``entry_points`` key.

Wires are defined under ``harness.wires`` key in entry points:

.. code-block:: python

  setup(
      name='your-package',
      ...
      entry_points={
          'harness.wires': [
              'python/logging=harness.wires.logging',
          ],
      },
  )

Here is a corresponding proto-file example, which uses this wire:

.. code-block:: protobuf

  import "harness/wire.proto";
  import "harness/logging.proto";

  message Configuration {
      harness.logging.Console console = 3 [
          (harness.wire).input = "python/logging:ConsoleWire"
      ];
  }

When code-generation happens, Harness performs a lookup for ``python/logging``
location. By looking at entry points it knows that ``python/logging`` wires are
implemented in a ``harness.wires.logging`` module:

.. code-block:: python

  import harness.wires.logging

  @dataclass
  class WiresIn:
      console: harness.wires.logging.ConsoleWire

.. _pkg_resources: https://setuptools.readthedocs.io/en/latest/pkg_resources.html
