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

.. literalinclude:: source/status.proto
  :language: protobuf
  :caption: status.proto

It only defines one wire - HTTP server used to serve requests.

.. test::

  .. code-block:: console

    $ ls
    status.proto

Requirements
~~~~~~~~~~~~

In order to proceed, we have to install our runtime and build dependencies:

.. code-block:: console

  $ pip3 install "harness[sdk]" aiohttp

.. note:: These dependencies are great for development environments only, so:

  - You probably don't have to install ``aiohttp`` in CI environment
  - You certainly don't have to install ``[sdk]`` extras in runtime (production)
    environment

.. _code-generation:

Code Generation
~~~~~~~~~~~~~~~

Here we generate runtime for our service:

.. literalinclude:: source/generate.sh
  :language: sh

Runtime consists of an entrypoint and a wires definition:

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

Here we add our runtime configuration in the YAML format:

.. literalinclude:: source/status.yaml
  :language: yaml
  :caption: status.yaml

Content of this file should conform to the ``Configuration`` message definition
in the ``status.proto`` file.

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

Here we add implementation of our service:

.. literalinclude:: source/status.py
  :language: python3

It must contain a ``setup`` coroutine function, which accepts configuration and
initialized input wires, and returns output wires. Everything else is up to you.

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

Finish
~~~~~~

Now we can launch our service:

.. code-block:: console

  $ python3 entrypoint.py --help
  usage: entrypoint.py [-h] [--merge MERGE] [--patch PATCH] config

  positional arguments:
    config         Configuration file in the YAML format

  optional arguments:
    -h, --help     show this help message and exit
    --merge MERGE  Merge config with a file
    --patch PATCH  Patch config with a file
  $ python3 entrypoint.py status.yaml

Open http://localhost:8000/ url and check that your service is up and running.
Now you can add more wires and implement your logic.

.. test::

  .. code-block:: console

    $ curl http://localhost:8000/
    OK

.. note:: Every time you change your configuration in the ``status.proto`` file,
  you must regenerate your runtime (see :ref:`code-generation` section above).
