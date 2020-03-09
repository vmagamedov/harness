Python Guide
============

We start with an empty directory on the file system.

.. code-block:: console

  $ mkdir status
  $ cd status

Service Configuration
~~~~~~~~~~~~~~~~~~~~~

You can use :doc:`../bootstrap` page to start configuring your service.
Here is our initial minimal configuration:

.. code-block:: protobuf
  :caption: status.proto

  syntax = "proto3";

  package status;

  import "harness/wire.proto";
  import "harness/http.proto";

  message Configuration {
      option (harness.service).name = "status";

      harness.http.Server server = 1 [
          (harness.wire).output.type = "harness.wires.aiohttp.web.ServerWire"
      ];
  }

.. test::

  .. code-block:: console

    $ ls
    status.proto

Code Generation
~~~~~~~~~~~~~~~

.. code-block:: console

  $ protoc -I. -I$(harness proto-path) --harness_out=python:. --python_out=.

.. test::

  .. code-block:: console
    :emphasize-lines: 3-5

    $ ls
    status.proto
    status_pb2.py
    status_wires.py
    entrypoint.py

Runtime Configuration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml
  :caption: status.yaml

  server:
    bind:
      host: 0.0.0.0
      port: 8000

.. test::

  .. code-block:: console
    :emphasize-lines: 6

    $ ls
    status.proto
    status_pb2.py
    status_wires.py
    entrypoint.py
    status.yaml


Service Implementation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python3

  from aiohttp import web
  from harness.wires.aiohttp.web import ServerWire

  from status_pb2 import Configuration
  from status_wires import WiresIn, WiresOut

  async def index(request):
      return web.Response(text='OK')

  async def setup(config: Configuration, wires_in: WiresIn) -> WiresOut:
      app = web.Application()
      app.router.add_get('/', index)
      return WiresOut(server=ServerWire(app))

.. test::

  .. code-block:: console
    :emphasize-lines: 7

    $ ls
    status.proto
    status_pb2.py
    status_wires.py
    entrypoint.py
    status.yaml
    status.py

Entrypoint
~~~~~~~~~~

.. code-block:: console

  $ python3 entrypoint.py status.yaml
