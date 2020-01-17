import time

from global_id import Node, GlobalIdError

node = Node(0)

result_count = {}
error_count = {}

while len(result_count) < 5:
    # use the same time to make sure we're aligned
    second = int(node.time())

    try:
        node.get_id()
        result_count[second] = result_count.get(second, 0) + 1
    except GlobalIdError:
        error_count[second] = error_count.get(second, 0) + 1

print("second results errors")
for second in sorted(result_count):
    print(second, result_count[second], error_count.get(second, 0))

# TODO: why isn't the first second all errors, though?

