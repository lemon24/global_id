"""
A node in a system that generates ids guaranteed to be globally unique.

The system is composed of a fixed number of nodes, represented by a numeric id.
Each node runs one process serving ids. Each node knows its id at startup 
and that id never changes for the node.

:class:`Node` holds the state and logic for such a node.


Id structure
------------

In the default configuration, the generated ids are 64-bit non-negative 
integers with the following format::

    | time part (37 bits) | sequence (17 bits) | node id (10 bits) |

The time part represents seconds since an epoch specific to the system,
and makes the ids generated in different seconds unique. 
Unique ids can be generated for 2**37 seconds = ~4355 years.

The sequence makes ids generated within the same second unique.
This allows for a maximum of 2**17 = ~131K ids / second / node.
Once the possible ids for a second are exhausted, an exception is raised.

The node id makes ids generated by different nodes unique. There can be
up to 1024 nodes. It is assumed that the node id does not change for a 
running node, and that no more than 1 node with a specific id exists
at any given point in time.

The maximum time, ids per second, number of nodes, and the total bit
length of the generated ids can be adjusted by changing the 
{time_part,sequence,node_id}_bits Node attributes.


Assumptions
-----------

TODO: node id uniqueness

TODO: clock synchronization


Subnodes
--------

TODO: subnodes


Acknowledgements
----------------

TODO: snowflake

"""

import time
import math
import datetime
from typing import Tuple, ClassVar, TYPE_CHECKING

# Final appears in the typing module only in Python 3.8, and we don't want
# to force people to install typing_extensions (mypy always depends on it).
if TYPE_CHECKING:  # pragma: no cover
    from typing_extensions import Final
else:
    Final = "Final"


# TODO: better exception names + docstrings


class GlobalIdError(Exception):
    pass


class OutOfIds(GlobalIdError):
    pass


class OutOfSeconds(GlobalIdError):
    pass


class ClockError(GlobalIdError):
    pass


class Node:

    """
    A node in a system that generates ids guaranteed to be globally unique.
    
    See the module docstring for details.
    
    Args:
        node_id (int): The node id, in range(1024).
        subnode_id (int): The subnode id, in range(subnode_count).
        subnode_count (int): The subnode count, must be positive.

    """

    # TODO: account for some desync

    time_part_bits: ClassVar = 37
    sequence_bits: ClassVar = 17
    node_id_bits: ClassVar = 10

    time_part_epoch: ClassVar = int(
        datetime.datetime(2020, 1, 1).replace(tzinfo=datetime.timezone.utc).timestamp()
    )

    def __init__(
        self, node_id: int, subnode_id: int = 0, subnode_count: int = 1,
    ):
        if node_id < 0 or node_id.bit_length() > self.node_id_bits:
            raise ValueError(
                f"node_id must be a non-negative integer lower than "
                f"{2 ** self.node_id_bits - 1}, got: {node_id}"
            )
        self._node_id: Final = node_id

        if subnode_count <= 0:
            raise ValueError(
                f"subnode_count must be a positive integer, got: {subnode_count}"
            )
        if not (0 <= subnode_id < subnode_count):
            raise ValueError(
                f"subnode_id must be a non-negative integer lower than "
                f"subnode_count, got: {subnode_id}"
            )

        self._subnode_id: Final = subnode_id
        self._subnode_count: Final = subnode_count

        # we don't want to emit any ids for the current second,
        # since we don't know the sequence for it, so we consider it exhausted
        self._last_now = self.time()
        self._last_sequence = 2 ** self.sequence_bits

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
        # TODO: explain why this is not in get_id

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

        if now < last_now:
            raise ClockError(f"clock moved backwards")
        if now < cls.time_part_epoch:
            raise ClockError(f"current time behind node epoch")

        second = math.floor(now) - cls.time_part_epoch
        if second.bit_length() > cls.time_part_bits:
            raise OutOfSeconds(f"maximum seconds since epoch exceeded: {second}")

        last_second = math.floor(last_now) - cls.time_part_epoch

        if last_second != second:
            sequence = subnode_id
        else:
            sequence = last_sequence + subnode_count

        if sequence.bit_length() > cls.sequence_bits:
            raise OutOfIds(f"ran out of ids for this second: {second}")

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
