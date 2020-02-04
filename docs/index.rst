.. toctree::
  :hidden:

  configuration
  runtime

.. toctree::
  :hidden:
  :caption: Python

  python/index

Introduction
~~~~~~~~~~~~

Harness is a language-agnostic meta-framework for building a serverless-style
services:

  - it lets you glue together other frameworks, libraries and your own code to
    build a solution which fits your needs
  - serverless means that Harness ships with a :doc:`runtime <runtime>`, which
    you can use to run your services
  - you can use Harness to generate deploy configuration for your services
  - to make all this happen, Harness uses a language-agnostic self-describing
    :doc:`configuration format <configuration>`

Motivation
~~~~~~~~~~

It doesn't matter which programming language you use, all services have many
things in common:

  - configuration
  - secrets
  - startup and shutdown sequences
  - logs, metrics, tracing
  - deploy configuration

Any great service have to have all of this, implemented in a best way.

Obvious way is to use a scaffolding tool to setup every new project. But then
you have to support all of this in every service by yourself.

Harness takes another approach, it manages all of this all the time for you.

Philosophy
~~~~~~~~~~

:doc:`Configuration <configuration>` is a source of truth. It can explain
a lot of things.

Installation
~~~~~~~~~~~~

.. code-block:: console

  $ pip3 install harness
  $ brew install protobuf
