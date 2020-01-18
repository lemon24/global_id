from global_id import Node
import time

if __name__ == '__main__':
    node = Node(4)
    for i in range(10):
        
        try:
            print(node._last_now, node._last_sequence, node._get_id())
        except Exception as e:
            print(node._last_now, node._last_sequence, f"{type(e).__name__}: {e}")
            
        time.sleep(.2)
            
