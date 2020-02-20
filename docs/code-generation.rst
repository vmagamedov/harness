Code Generation
===============

We use ``protoc`` compiler to generate :doc:`runtime <runtime>` parts from your
:doc:`configuration <configuration>`. Here is an example of how to generate
code for a ``python`` runtime:

.. code-block:: console

  $ protoc -I$(harness proto-path) --harness_out=python:./src ./src/service.proto
                                                 ^----^
                                                 runtime
