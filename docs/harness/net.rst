harness/net.proto
=================

.. proto:message:: harness.net.Socket

  .. proto:field:: string host

  .. proto:field:: uint32 port

.. proto:message:: harness.net.Pipe

  .. proto:field:: string name

  .. proto:field:: uint32 mode

.. proto:message:: harness.net.Address

  .. proto:field:: harness.net.Socket socket

  .. proto:field:: string pipe

.. proto:message:: harness.net.Server

  .. proto:field:: harness.net.Socket bind

