harness/http.proto
==================

.. proto:package:: harness.http

.. proto:message:: Connection

  Used to configure HTTP client connections

  .. proto:field:: harness.net.Socket address

    TCP address of a server

.. proto:message:: Server

  Used to configure HTTP servers

  .. proto:field:: harness.net.Socket bind

    TCP address to bind and listen for client connections

