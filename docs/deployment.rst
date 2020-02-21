Deployment
==========

Here is how to generate Kubernetes manifests from your service definition:

.. code-block:: console

  $ harness kube-gen service.proto python service.yaml v2020
                     ^-----------^ ^----^ ^----------^ ^---^
                           1         2         3         4

1. Configuration's definition location
2. Runtime name
3. Configuration runtime values
4. Version

Additional options:

--instance
  Instance of your deployment -- ``app.kubernetes.io/instance``, when you have
  to deploy several instances of your service into the same namespace
--namespace
  Explicitly defines a namespace in the manifests
--secret-merge
  Path to a YAML file with a secrets defined in the `JSON Merge Patch`_ format
--secret-patch
  Path to a YAML file with a secrets defined in the `JSON Patch`_ format
--base-domain
  If you have an output ``PUBLIC`` wire of :proto:message:`harness.http.Server`
  type, Harness also generates a routing config to accept ingress traffic from
  ``https://{service-name}.{base-domain}`` domain, where ``service-name``
  comes from a ``(harness.service).name`` option value

  .. note:: ``--instance`` option value is added as a suffix to the sub-domain

Kubectl
~~~~~~~

.. code-block:: console

  $ harness kube-gen {...args...} | kubectl apply -f -

Kustomize
~~~~~~~~~

.. code-block:: console

  $ harness kube-gen {...args...} > deployment.yaml
  $ kubectl apply -k .

.. _JSON Merge Patch: https://tools.ietf.org/html/rfc7386
.. _JSON Patch: https://tools.ietf.org/html/rfc6902
