harness/net.proto
=================

.. proto:package:: harness.net

.. proto:message:: Socket

  Used to configure TCP sockets

  .. proto:field:: string host

    IP address or domain name

  .. proto:field:: uint32 port

    Port number

.. proto:message:: Pipe

  Used to configure Unix domain sockets

  .. proto:field:: string name

    Path on the file system

  .. proto:field:: uint32 mode

    File access permissions

.. proto:message:: Address

  .. proto:field:: harness.net.Socket socket

  .. proto:field:: string pipe

.. proto:message:: Server

  Used to configure TCP servers

  .. proto:field:: harness.net.Socket bind

    TCP address to bind and listen for client connections

