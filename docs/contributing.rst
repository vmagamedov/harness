Contributing
============

Contributions are highly welcomed and appreciated.

Style Guide
~~~~~~~~~~~

This project uses black_ for formatting and flake8_ for linting. These tools
are used in a pre-commit hook. Here is how to enable them:

.. code-block:: console

  $ pip install pre-commit
  $ pre-commit install
  pre-commit installed at .git/hooks/pre-commit

Optionally you can invoke pre-commit explicitly after you staged your changes
and before you're ready to commit:

.. code-block:: console

  $ pre-commit
  black....................................................................Passed
  flake8...................................................................Passed

You can also invoke black_ and flake8_ explicitly:

.. code-block:: console

  $ pip install -r requirements/check.txt
  $ black .
  All done! ✨ 🍰 ✨
  49 files left unchanged.
  $ flake8

Tests
~~~~~

This project uses pytest_ framework and tox_ automation:

.. code-block:: console

  $ pip install tox
  $ tox -e py37

Or to run pytest_ explicitly:

.. code-block:: console

  $ pip install -r requirements/test.txt
  $ pytest
  ..................................................                       [100%]
  50 passed in 0.58s

.. _black: https://black.readthedocs.io
.. _flake8: https://flake8.pycqa.org
.. _pytest: https://pytest.org
.. _tox: https://tox.readthedocs.io
