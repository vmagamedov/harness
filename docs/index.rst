.. toctree::
  :hidden:

  configuration
  code-generation
  runtime
  reference

.. toctree::
  :hidden:
  :caption: Python

  python/index

Introduction
~~~~~~~~~~~~

Harness is a language-neutral meta-framework for building serverless-style
services:

- It lets you glue together other frameworks, libraries and your own code to
  build a solution which fits your needs
- Serverless means that Harness ships with a :doc:`runtime <runtime>`, which
  you can use to run your services
- You can use Harness to generate deploy configuration for your services
- To make all this happen, Harness uses a language-neutral self-describing
  :doc:`configuration format <configuration>`

Motivation
~~~~~~~~~~

It doesn't matter which programming language you use, all services have many
things in common, like:

- Configuration management
- Secrets management
- Startup and shutdown sequences
- Logs, metrics, tracing
- Deploy configuration

Every service have to have all of this, implemented in a consistent and
reasonable way.

Obvious way is to use a scaffolding tool to setup every new project. But then
you have to support all of this in every service by yourself. Harness takes
another approach, it manages all of this all the time for you.

Philosophy
~~~~~~~~~~

- :doc:`Configuration <configuration>` in Harness is a source of truth.
  It explicitly defines what your service is capable to do
- Harness utilises code-generation to translate this configuration into source
  code, then you add your code on top of it
- Such configuration opens many possibilities, that's why Harness is also
  capable to generate a deploy configuration (e.g. Kubernetes manifests)
- Harness provides wires for different libraries and frameworks, and you can
  write your own wires. So there is no single true way and no limitations

Installation
~~~~~~~~~~~~

.. code-block:: console

  $ pip3 install harness
  $ brew install protobuf
