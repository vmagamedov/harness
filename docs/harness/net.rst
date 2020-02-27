harness/net.proto
=================

.. proto:package:: harness.net

.. proto:message:: Socket

  .. proto:field:: string host

  .. proto:field:: uint32 port

.. proto:message:: Pipe

  .. proto:field:: string name

  .. proto:field:: uint32 mode

.. proto:message:: Address

  .. proto:field:: harness.net.Socket socket

  .. proto:field:: string pipe

.. proto:message:: Server

  .. proto:field:: harness.net.Socket bind

