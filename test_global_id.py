import pytest

from global_id import Node, GlobalIdError, OutOfIds, OutOfSeconds


class FakeTimeMixin:

    time_part_epoch = 0

    def __init__(self, *args, **kwargs):
        self.now = -1
        super().__init__(*args, **kwargs)

    def time(self):
        return self.now

    def exhaust(self):
        def exhaust_sequence():
            while True:
                try:
                    yield self._get_id()
                except OutOfIds:
                    break

        def exhaust_seconds():
            while True:
                self.now += 1
                try:
                    yield list(exhaust_sequence())
                except OutOfSeconds:
                    break

        return list(exhaust_seconds())


class TinyNode(FakeTimeMixin, Node):
    time_part_bits = 1
    sequence_bits = 2
    node_id_bits = 3


TINY_NODE_TUPLE_IDS = {
    (0, 1): [[(0, 0), (0, 1), (0, 2), (0, 3)], [(1, 0), (1, 1), (1, 2), (1, 3)],],
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


def args_items_ids(argvalue):
    if isinstance(argvalue, tuple):
        subnode_id, subnode_count = argvalue
        return f"subnode_{subnode_id}_{subnode_count}"
    return "<subnode_ids>"


@pytest.mark.parametrize(
    "args, expected_ids", list(TINY_NODE_TUPLE_IDS.items()), ids=args_items_ids,
)
@pytest.mark.parametrize("node_id", list(range(2 ** 3)))
def test_tiny_node_tuple_ids(node_id, args, expected_ids):
    actual = TinyNode(node_id, *args).exhaust()
    expected = [
        [(time_part, sequence, node_id) for time_part, sequence in id_list]
        for id_list in expected_ids
    ]
    assert actual == expected
