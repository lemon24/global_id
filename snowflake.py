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

"""

import time


class GlobalIdError(Exception): pass


class GlobalIdBase:

    """
    A guaranteed globally unique id system.

    # TODO: explain usage

    """

    TIMESTAMP_BITS = 37
    SEQUENCE_BITS = 17
    NODE_ID_BITS = 10

    def __init__(self):
        self._last_sequence = 0
        self._last_second = 0

    def timestamp(self) -> int:
        """Return timestamp since the epoch in milliseconds."""
        raise NotImplementedError

    def node_id(self) -> int:
        """Return the node id as a globally-unique integer 0 <= id <= 1023."""
        raise NotImplementedError

    def get_id(self) -> int:
        now = self.timestamp()
        second = now // 1000

        if self._last_sequence >= 2 ** cls.SEQUENCE_BITS - 1:
            if self._last_second == second:
                raise GlobalIdError("ran out of ids for this second")
            self._last_sequence = 0
        else:
            self._last_sequence += 1

        self._last_second = second

        return self._make_id(second, self._last_sequence, self.node_id())

    @classmethod
    def _make_id(cls, timestamp: int, sequence: int, node_id: int) -> int:
        # TODO: docstring

        assert timestamp < 2 ** cls.TIMESTAMP_BITS
        assert sequence < 2 ** cls.SEQUENCE_BITS
        assert node_id < 2 ** cls.NODE_ID_BITS

        id = timestamp
        id <<= cls.SEQUENCE_BITS
        id |= sequence
        id <<= cls.NODE_ID_BITS
        id |= node_id

        return id


class GlobalId(GlobalIdBase):

    def __init__(self, node_id: int):
        super().__init__()
        self._node_id = node_id

    @staticmethod
    def timestamp() -> int:
        return int(time.time() * 1000)

    def node_id(self):
        return self._node_id

