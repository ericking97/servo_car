class Node:
    """
    Linked List element
    """
    data: int
    prev: "Node | None"
    next: "Node | None"

    def __init__(self, data: int):
        self.data = data
        self.prev = None
        self.next = None
