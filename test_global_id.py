import pytest

from global_id import Node, GlobalIdError, OutOfIds, OutOfSeconds


class FakeTimeMixin:

    initial_now = -1

    def __init__(self, *args, **kwargs):
        self.now = self.initial_now
        super().__init__(*args, **kwargs)

    def time(self):
        return self.now

    def get_all(self, get_id=lambda n: n._get_id()):
        """Return all the possible ids for the node as a list of lists,
        each inner list containing the ids for a different time_part.

        >>> class MyNode(FakeTimeMixin, Node):
        ...     time_part_bits = 3
        ...     sequence_bits = 3
        ...     node_id_bits = 3
        ...     time_part_epoch = 0
        ...
        >>> MyNode(0).get_all(lambda n: n._get_id())
        [
            [(0, 0, 0), (0, 1, 0), (0, 2, 0), ...],
            [(1, 0, 0), (1, 1, 0), (1, 2, 0), ...],
            [(2, 0, 0), (2, 1, 0), (2, 2, 0), ...],
            ...
        ]

        """

        def sequence():
            while True:
                try:
                    yield get_id(self)
                except OutOfIds:
                    break

        def all():
            while True:
                self.now += 1
                try:
                    yield list(sequence())
                except OutOfSeconds:
                    break

        return list(all())


class FakeTimeNode(FakeTimeMixin, Node):
    time_part_epoch = 0


class TinyNode(FakeTimeMixin, Node):
    time_part_bits = 1
    sequence_bits = 2
    node_id_bits = 3
    time_part_epoch = 0


# TinyNode.get_all() output for various subnode_{id,count}s,
# but missing the node_id (since it should never change).
#
# (subnode_id, subnode_count): [
#   [(time_part, sequence), (time_part, sequence + 1), ...],
#   [(time_part + 1, sequence), (time_part + 1, sequence + 1), ...],
#   ...
# ]
#
TINY_NODE_TUPLE_IDS = {
    (0, 1): [[(0, 0), (0, 1), (0, 2), (0, 3)], [(1, 0), (1, 1), (1, 2), (1, 3)]],
    (0, 2): [[(0, 0), (0, 2)], [(1, 0), (1, 2)]],
    (1, 2): [[(0, 1), (0, 3)], [(1, 1), (1, 3)]],
    (0, 3): [[(0, 0), (0, 3)], [(1, 0), (1, 3)]],
    (1, 3): [[(0, 1)], [(1, 1)]],
    (2, 3): [[(0, 2)], [(1, 2)]],
    (0, 4): [[(0, 0)], [(1, 0)]],
    (1, 4): [[(0, 1)], [(1, 1)]],
    (2, 4): [[(0, 2)], [(1, 2)]],
    (3, 4): [[(0, 3)], [(1, 3)]],
    (0, 5): [[(0, 0)], [(1, 0)]],
    (1, 5): [[(0, 1)], [(1, 1)]],
    (2, 5): [[(0, 2)], [(1, 2)]],
    (3, 5): [[(0, 3)], [(1, 3)]],
    (4, 5): [[], []],
}


def format_tuple_ids(value):
    if isinstance(value, tuple):
        subnode_id, subnode_count = value
        return f"subnode_{subnode_id}_{subnode_count}"
    return "<subnode_ids>"


@pytest.mark.parametrize(
    "args, expected_ids", list(TINY_NODE_TUPLE_IDS.items()), ids=format_tuple_ids,
)
@pytest.mark.parametrize("node_id", list(range(2 ** 3)))
def test_tiny_node_tuple_ids(node_id, args, expected_ids):
    node = TinyNode(node_id, *args)
    actual = node.get_all()
    expected = [[id + (node_id,) for id in id_list] for id_list in expected_ids]
    assert actual == expected


def test_tiny_node_int_ids():
    node = TinyNode(2, 0, 1)
    assert node.get_all(lambda n: n.get_id()) == [
        [0b000010, 0b001010, 0b010010, 0b011010],
        [0b100010, 0b101010, 0b110010, 0b111010],
    ]


def test_default_subnode_args():
    assert TinyNode(7).get_all() == TinyNode(7, 0, 1).get_all()


def test_init_errors():
    with pytest.raises(ValueError):
        Node(-1)
    Node(0)
    Node(1023)
    with pytest.raises(ValueError):
        Node(1024)

    with pytest.raises(ValueError):
        Node(0, subnode_count=-1)
    with pytest.raises(ValueError):
        Node(0, subnode_count=0)

    with pytest.raises(ValueError):
        Node(0, subnode_id=-1, subnode_count=1)
    Node(0, subnode_id=0, subnode_count=1)
    with pytest.raises(ValueError):
        Node(0, subnode_id=1, subnode_count=1)

    with pytest.raises(ValueError):
        Node(node_id=0, subnode_id=-1, subnode_count=2)
    Node(node_id=0, subnode_id=0, subnode_count=2)
    Node(node_id=0, subnode_id=1, subnode_count=2)
    with pytest.raises(ValueError):
        Node(node_id=0, subnode_id=2, subnode_count=2)


# TODO: test time_part_epoch
# TODO: test clock errors (clock moved backwards, clock behind epoch)
# TODO: test there are no ids for the first second
# TODO: test a bunch of real ids, including edges
# TODO: test a bunch of real ids with subnodes
# TODO: test default time()
