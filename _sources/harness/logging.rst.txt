harness/logging.proto
=====================

.. proto:package:: harness.logging

.. proto:enum:: Level

  .. proto:value:: NOTSET

  .. proto:value:: DEBUG

  .. proto:value:: INFO

  .. proto:value:: WARNING

  .. proto:value:: ERROR

  .. proto:value:: CRITICAL

.. proto:message:: Console

  .. proto:enum:: Stream

    .. proto:value:: STDERR

    .. proto:value:: STDOUT

  .. proto:field:: harness.logging.Console.Stream stream

  .. proto:field:: harness.logging.Level level

.. proto:message:: Syslog

  .. proto:enum:: Facility

    .. proto:value:: NOTSET

    .. proto:value:: USER

    .. proto:value:: LOCAL0

    .. proto:value:: LOCAL1

    .. proto:value:: LOCAL2

    .. proto:value:: LOCAL3

    .. proto:value:: LOCAL4

    .. proto:value:: LOCAL5

    .. proto:value:: LOCAL6

    .. proto:value:: LOCAL7

  .. proto:field:: string app

  .. proto:field:: harness.logging.Syslog.Facility facility

  .. proto:field:: harness.logging.Level level

