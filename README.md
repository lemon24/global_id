Solution to an interview project: (part of) a system that generates ids
guaranteed to be globally unique; see [problem.md](./problem.md) for
the full problem description.

The main implementation is in [global_id.py](./global_id.py).
A simple UDP server wrapping it can be found in
[global_id_udp.py](./global_id_udp.py).

All the code should work on Python >=3.6.9 (both CPython and PyPy).

To install development dependencies, run the following (preferably inside a
[virtual environment](https://docs.python.org/3/library/venv.html)):

    make install-dev

To run the tests:

    make test
    make coverage  # same as test, but generates a coverage report in htmlcov/

To run the static type checker:

    make typing





