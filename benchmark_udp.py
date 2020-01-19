"""
Measure how many ids/second a Node can generate via UDP.

We are using multiple processes for the following reasons:

* Python and/or the kernel are not sending/receiving packets fast enough;
  see the global_id_udp.run_server() docstring for details.

* If Node.get_id() is too slow this spreads the load; according to
  benchmark_simple.py this should not be the case, but it can help 
  if it gets slower in the future.

We are using processes and not threads to work around the GIL;
https://docs.python.org/3/glossary.html#term-global-interpreter-lock

"""
import socket
import time
import multiprocessing

from global_id_udp import run_server, get_id


def do_requests(addr):
    """Make as many id requests as possible to addr, forever.

    Yields:
        tuple(int, int): (ok count, error count) tuples, roughly every second.

    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(addr)

        start = time.monotonic()

        ok_error_counts = [0, 0]
        while True:
            status, *_ = get_id(sock)
            ok_error_counts[status] += 1

            end = time.monotonic()
            if end - start > 1:
                yield ok_error_counts
                ok_error_counts = [0, 0]

                start = end


def exit_on_keyboard_interrupt(func, args):
    try:
        func(*args)
    except KeyboardInterrupt:
        pass


def start_in_processes(process_count, func, *args):
    """Run func in multiple processes.

    Returns on KeyboardInterrupt.

    Args:
        process_count (int): The number of processes to start.
        func (callable): Called as func(process_id, process_count, *args).
        args (tuple): Will be passed to func.
        
        
    Returns:
        list(multiprocessing.Process)

    """
    processes = []

    for i in range(process_count):
        process = multiprocessing.Process(
            target=exit_on_keyboard_interrupt, args=(func, (i, process_count, *args))
        )
        processes.append(process)
        process.start()

    return processes


def run_server_wrapper(process_id, process_count, addr, node_id):
    run_server(addr, node_id, process_id, process_count)


def consume_response_stats(process_id, process_count, addr, queue):
    for stats in do_requests(addr):
        queue.put(stats)


def do_benchmark(addr, process_count):
    start_in_processes(process_count, run_server_wrapper, addr, 0)

    queue = multiprocessing.Queue()
    start_in_processes(process_count, consume_response_stats, addr, queue)

    while True:
        ok_counts = []
        error_counts = []
        for _ in range(process_count):
            ok_count, error_count = queue.get()
            ok_counts.append(ok_count)
            error_counts.append(error_count)
        print(
            f"ok: {sum(ok_counts)}, error: {sum(error_counts)}; "
            f"ok: {ok_counts}, error: {error_counts}"
        )


if __name__ == "__main__":
    addr = ("127.0.0.1", 9999)

    import sys

    if len(sys.argv) > 1:
        process_count = int(sys.argv[1])
    else:
        process_count = multiprocessing.cpu_count()

    do_benchmark(addr, process_count)
