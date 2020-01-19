"""
Simple UDP request-response server wrapper over global_id.Node, mainly for
seeing how many ids/second it can generate in an environment similar to
the real world.

It is *not* production ready in any way, and has at least the following issues:

* two different clients can get the same id because of duplicate UDP packets
  (possible fix: tag requests/responses in some way so the client can check
  it got the response it was waiting for)

* a client may not get the id it was waiting for due to lost UDP packets
  (possible fixes: use a connection-oriented protocol, client retries)

Requests look like::

    | 0 (8 bits) |
    
Successful responses look like::

    | 0 (8 bits) | id (64 bits) |
    
Error responses look like::

    | 1 (8 bits) |

"""

import socket
import struct

from global_id import Node, GlobalIdError


def unpack_response(data):
    (status,) = struct.unpack_from("!B", data)
    if status != 0:
        return (status,)
    (id,) = struct.unpack("!Q", data[struct.calcsize("!B") :])
    return status, id


def pack_response_ok(id):
    return struct.pack("!BQ", 0, id)


def pack_response_error():
    return struct.pack("!B", 1)


def unpack_request(data):
    (request,) = struct.unpack("!B", data)
    if request != 0:
        raise ValueError("bad request")
    return request


def pack_request():
    return struct.pack("!B", 0)


def run_server(addr, *args):
    """Bind to addr and serve id requests forever.

    The socket has the SO_REUSEPORT option, so multiple servers can serve
    requests on the same port. On Linux, each server should get a separate
    socker descriptor with a dedicated receive buffer, and the requests
    should be spread evenly across them:

    * https://blog.cloudflare.com/how-to-receive-a-million-packets/
    * https://lwn.net/Articles/542629/

    Args:
        addr: Passed to socket.bind(addr).
        *args: Passed to Node(*args).

    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)
    sock.bind(addr)

    node = Node(*args)

    while True:
        request_data, addr = sock.recvfrom(1024)

        try:
            unpack_request(request_data)
            response_data = pack_response_ok(node.get_id())
        except (ValueError, struct.error) as e:
            response_data = pack_response_error()
        except GlobalIdError as e:
            response_data = pack_response_error()

        sock.sendto(response_data, addr)


def get_id(sock):
    """Given a socket connected to an UDP server, request an id and return it.

    Args:
        sock: A connected socket.

    Returns:
        tuple(int) or tuple(int, int): (0, id) on success, (1, ) on error.

    """
    sock.send(pack_request())
    return unpack_response(sock.recv(1024))


if __name__ == "__main__":
    import time
    import threading

    addr = ("127.0.0.1", 9999)

    threading.Thread(target=run_server, args=(addr, 0), daemon=True).start()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(addr)

        print(get_id(sock))
        time.sleep(1)
        print(get_id(sock))
