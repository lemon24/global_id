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
import datetime
from typing import Tuple


class GlobalIdError(Exception):
    pass


class OutOfIds(GlobalIdError):
    pass


class ClockError(GlobalIdError):
    pass


class GlobalId:

    """
    A guaranteed globally unique id system.

    # TODO: explain usage
    Arguments:

    The node id as a globally-unique integer 0 <= id <= 1023.

    """

    time_part_bits = 37
    sequence_bits = 17
    node_id_bits = 10

    time_part_epoch = int(
        datetime.datetime(2020, 1, 1).replace(tzinfo=datetime.timezone.utc).timestamp()
    )

    def __init__(
        self, node_id: int, subnode_id: int = 0, subnode_count: int = 1,
    ):
        if node_id > 2 ** self.node_id_bits - 1:
            raise ValueError(f"node_id greater than expected: {node_id}")
        if node_id < 0:
            raise ValueError(f"node_id must be a non-negative integer: {node_id}")
        self._node_id = node_id

        if subnode_count < 0:
            raise ValueError(f"subnode_count must be a non-negative integer")
        if not (0 <= subnode_id < subnode_count):
            raise ValueError(f"subnode_ide must be an integer in [0, subnode_count)")

        self._subnode_id = subnode_count
        self._subnode_count = subnode_count

        # we don't want to emit any ids for the current second,
        # since we don't know the sequence for it, so we consider it exhausted
        self._last_now = self.time()
        self._last_sequence = 2 ** self.sequence_bits - 1

    @staticmethod
    def time() -> float:
        """Return the time since the Unix epoch."""
        return time.time()

    def get_id(self) -> int:
        """Return a new id.

        Raises:
            GlobalIdError
        """
        return self._pack_id(*self._get_id())

    def _get_id(self) -> Tuple[int, int, int]:
        """Return a new id as a (time_part, sequence, node_id) tuple,
        advancing the generator state as needed.

        """
        now = self.time()

        time_part, sequence = self._next(
            now,
            self._last_now,
            self._last_sequence,
            self._subnode_id,
            self._subnode_count,
        )

        self._last_now = now
        self._last_sequence = sequence

        return time_part, sequence, self._node_id

    @classmethod
    def _next(
        cls,
        now: float,
        last_now: float,
        last_sequence: int,
        subnode_id: int,
        subnode_count: int,
    ) -> Tuple[int, int]:
        """Starting from the previous state, return the next (time_part, sequence)."""

        if last_now > now:
            raise ClockError(f"clock moved backwards")

        second = int(now) - cls.time_part_epoch

        if second > 2 ** cls.time_part_bits - 1:
            raise OutOfIds(f"maximum seconds since epoch exceeded: {second}")

        sequence = last_sequence + subnode_count

        if sequence >= 2 ** cls.sequence_bits - 1:
            if int(last_now) == second:
                raise OutOfIds(f"ran out of ids for this second: {second}")
            sequence = subnode_id

        return second, sequence

    @classmethod
    def _pack_id(cls, time_part: int, sequence: int, node_id: int) -> int:
        """Pack a time_part, sequence, node_id into an int."""
        id = time_part
        id <<= cls.sequence_bits
        id |= sequence
        id <<= cls.node_id_bits
        id |= node_id
        return id
