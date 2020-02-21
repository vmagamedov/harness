Wires
=====

This is the main concept of the Harness. Every service needs to communicate
with the outside world. And every communication type have to be defined and
configured.

Wire Types
~~~~~~~~~~

There are two wire types:

- Input wires
- Output wires

We plug input wire when we want to **request** other service, e.g. database.

We plug output wire when we want to **provide** a service, e.g. serve HTTP API.

That is why :doc:`runtime` passes input wires as an argument to your setup
function, and accepts output wires as a return value of that function.

Input Wires
~~~~~~~~~~~

Output Wires
~~~~~~~~~~~~
