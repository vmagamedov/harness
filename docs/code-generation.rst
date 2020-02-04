Code Generation
===============

We use ``protoc`` compiler to generate boilerplate from your configuration:

.. code-block:: console

  $ protoc -I $HARNESS_PROTO --python_out=. --python_grpc_out=. --python_harness_out=. --mypy_out=. svc.proto

Where ``$HARNESS_PROTO`` is where to find `Harness` proto-files.
