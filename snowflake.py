"""
Imagine you are building a system to assign unique numbers to each resource
that you manage. You want the ids to be guaranteed unique i.e. no UUIDs.
Since these ids are globally unique, each id can only be given out at most once.
The ids are 64 bits long.

Your service is composed of a set of nodes, each running one process serving ids.
A caller will connect to one of the nodes and ask it for a globally unique id.
There are a fixed number of nodes in the system, up to 1024. Each node has a
numeric id, 0 <= id <= 1023. Each node knows its id at startup and that id
never changes for the node.

Your task is to implement get_id. When a caller requests a new id, the node
it connects to calls its internal get_id function to get a new, globally unique id.

Spent:

* 2020-01-06: 10:00, 10:30
* 2020-01-07: 9:00, 10:00
* 2020-01-08: 10:30, 11:00
 
"""

import time
from typing import Callable


class GlobalIdError(Exception): pass

class OutOfIdsError(GlobalIdError): pass


class GlobalIdBase:

    """
    A guaranteed globally unique id system. Ish.

    # TODO: explain usage
    Arguments:
    
    The node id as a globally-unique integer 0 <= id <= 1023.

    """

    TIMESTAMP_BITS = 37
    SEQUENCE_BITS = 17
    NODE_ID_BITS = 10

    def __init__(self, node_id: int, time: Callable[[], float] = time.time):
        if node_id > 2 ** cls.NODE_ID_BITS - 1:
            raise ValueError(f"node id greater than expected: {node_id}")

        self._node_id = node_id
        self._time = time

        # we don't want to emit any ids for the current second, 
        # since we don't know the sequence for it, so we consider it exhausted
        # TODO: should last_now be an argument, so we can wait an arbitrary time?
        self._last_now = self._time()
        self._last_sequence = 2 ** cls.SEQUENCE_BITS - 1

    #@staticmethod
    #def _time() -> float:
        #"""Return the time since the epoch."""
        #return time.time()

    def get_id(self) -> int:
        now = self._time()

        if self._last_now > now:
            raise OutOfIdsError(f"clock moved backwards")

        second = int(now)

        if second > 2 ** cls.TIMESTAMP_BITS - 1:
            raise GlobalIdError(f"maximum seconds since epoch exceeded: {second}")

        if self._last_sequence >= 2 ** cls.SEQUENCE_BITS - 1:
            if int(self._last_now) == second:
                raise OutOfIdsError(f"ran out of ids for this second: {second}")
            self._last_sequence = 0
        else:
            self._last_sequence += 1

        self._last_second = second

        return self._make_id(second, self._last_sequence, self._node_id)

    @classmethod
    def _make_id(cls, timestamp: int, sequence: int, node_id: int) -> int:
        id = timestamp
        id <<= cls.SEQUENCE_BITS
        id |= sequence
        id <<= cls.NODE_ID_BITS
        id |= node_id
        return id


# TODO: wrapper 
