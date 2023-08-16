============
Contributing
============

Thanks for considering contributing to PokerKit! Your contributions are
greatly appreciated, and help make PokerKit a better tool for everyone in
the Poker AI and research communities.

**Setting up Your Development Environment**
-------------------------------------------

1. Fork the PokerKit repository on GitHub.
2. Clone your fork locally: ``git clone git@github.com:username/pokerkit.git``
3. Setup virtual environment: ``python -m venv venv``
4. Activate the virtual environment: ``source venv/bin/activate``
5. Install requirements: ``pip install -r requirements.txt``
6. Create a branch for your changes: ``git checkout -b branch-name``

**Making Changes**
------------------

When making changes, please follow these guidelines:

- Always write your code in compliance with
  `PEP8 <https://peps.python.org/pep-0008/>`_.
- Write unit tests for your changes, and make sure all tests pass before
  submitting a pull request.
- Document your changes in the code and update the `README <README.rst>`_ file
  if necessary.
- After making changes, please validate your changes.

1. Run static type checking with ``--strict`` flag: ``mypy --strict pokerkit``
2. Run style checking: ``flake8 pokerkit``
3. Run unit tests: ``python -m unittest``
4. Run doctests: ``python -m doctest pokerkit/*.py``

**Submitting a Pull Request**
-----------------------------

1. Commit your changes: ``git commit -am 'Add some feature'``
2. Push to the branch: ``git push origin branch-name``
3. Submit a pull request to the ``main`` branch in the PokerKit repository.

Before submitting your pull request, please make sure the mypy static type
checking with ``--strict`` flag, flake8, doctests, unit tests pass, and your
code adheres to `PEP8 <https://peps.python.org/pep-0008/>`_.

**After Your Pull Request Is Merged**
-------------------------------------

After your pull request is merged, you can safely delete your branch and pull
the changes from the main repository:

- Delete the remote branch on GitHub: ``git push origin --delete branch-name``
- Check out the main branch: ``git checkout main``
- Delete the local branch: ``git branch -d branch-name``
- Update your main with the latest upstream version: ``git pull upstream main``
