Installation
============

Prerequisites
~~~~~~~~~~~~~

Harness SDK is written in Python and requires Python 3.7 or more recent version.
Here are some decent ways to get Python installed on your system.

Ubuntu
------

- You can use ``python3`` and ``python3-pip`` system packages since Ubuntu
  version 19.04

  .. code-block:: console

    $ sudo apt-get update
    $ sudo apt-get install python3 python3-pip
    $ pip3 --version
    pip 18.1 from /usr/lib/python3/dist-packages/pip (python 3.7)

- You can use ``python3.x`` system package from deadsnakes_ PPA if you have
  an older Ubuntu LTS version

  .. code-block:: console

    $ sudo apt-get update
    $ sudo apt-get install software-properties-common
    $ sudo add-apt-repository ppa:deadsnakes/ppa
    $ sudo apt-get install python3.7 python3.7-venv
    $ sudo python3.7 -m ensurepip
    $ pip3 --version
    pip 19.2.3 from /usr/local/lib/python3.7/dist-packages/pip (python 3.7)

macOS
-----

You can use Homebrew_ to install Python:

.. code-block:: console

  $ brew install python3
  $ pip3 --version
  pip 19.3.1 from /usr/local/lib/python3.7/site-packages/pip (python 3.7)

Windows
-------

You can use one of these guides:

- https://docs.python.org/3/using/windows.html
- https://docs.microsoft.com/en-us/windows/python/beginners

Development Kit
~~~~~~~~~~~~~~~

To get a latest stable version:

.. code-block:: console

  $ pip3 install "harness[sdk]"

New features and bug fixes are released often as release candidates:

.. code-block:: console

  $ pip3 install --pre "harness[sdk]"

.. _deadsnakes: https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa
.. _Homebrew: https://brew.sh
