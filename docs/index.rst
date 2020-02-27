Harness Framework
=================

.. toctree::
  :hidden:

  bootstrap
  configuration
  wires
  runtime
  code-generation
  deployment
  reference

.. toctree::
  :hidden:
  :caption: Runtimes

  python/index

Introduction
~~~~~~~~~~~~

Harness is a language-neutral meta-framework for building and deploying
serverless-style services:

- It glues together other libraries, frameworks and your own code
- Serverless-style means that Harness ships with a :doc:`runtime <runtime>`,
  which is used to run your services
- You can use Harness to generate deploy configuration for your services
- To make all this happen, Harness uses a language-neutral self-describing
  :doc:`configuration format <configuration>`

.. note:: Harness is in it's early stage of design and development.
  Please don't hesitate to provide your expertise in any form. Our goal is to
  develop a framework, which is not specific to some particular company, but
  to make it suitable for all, so everyone can benefit from it.

Motivation
~~~~~~~~~~

It doesn't matter which programming language you use, all services have many
things in common, like:

- Configuration management
- Secrets management
- Startup and shutdown strategy
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
