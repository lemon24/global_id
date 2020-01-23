Solution to an interview project: (part of) a system that generates ids
guaranteed to be globally unique.

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


## Performance

I managed to generate over 100K ids/second with a simple UDP server
using PyPy on a t3a.nano instance; see [performance.md](./performance.md)
for details.


## Answers to the problem questions

> 1. Please describe your solution to get_id and why it is correct i.e. guaranteed globally unique.

See [global_id.py](./global_id.py) docstring (Id structure).

> 2. Please explain how your solution achieves the desired performance i.e. 100,000 or more requests per second per node. How did you verify this?

See [performance.md](./performance.md).

> 3. Please enumerate possible failure cases and describe how your solution correctly handles each case.

See the [global_id.py](./global_id.py) docstring (Assumptions).

> How did you verify correctness? Some example cases:
>
> * How do you manage uniqueness after a node crashes and restarts?

See the [global_id.py](./global_id.py) docstring (Assumptions).

> * How do you manage uniqueness after the entire system fails and restarts?

See the [global_id.py](./global_id.py) docstring (Assumptions).

> * How do you handle software defects?

Automated tests:

* Tests for the implementation with smaller id sizes, for which we check
  exhaustively all the ids that can be generated.
* Tests that spot-check the real-size implementation.

Static type checking for the core of the implementation.

