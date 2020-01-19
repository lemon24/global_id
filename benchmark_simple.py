"""
Measure how many ids/second a Node can generate.

"""
import time

from global_id import Node, GlobalIdError


def do_requests(node):
    """Call node.get_id() as fast as possible, forever.

    Yields:
        tuple(int, int): (ok count, error count) tuples, roughly every second.

    """
    start = time.monotonic()

    ok_error_counts = [0, 0]
    while True:
        try:
            node.get_id()
            status = 0
        except GlobalIdError:
            status = 1

        ok_error_counts[status] += 1

        end = time.monotonic()
        if end - start > 1:
            yield ok_error_counts
            ok_error_counts = [0, 0]

            start = end


def do_benchmark():
    node = Node(0)

    for ok_count, error_count in do_requests(node):
        print(f"ok: {ok_count}, error: {error_count}")


if __name__ == "__main__":
    import sys

    try:
        do_benchmark()
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
