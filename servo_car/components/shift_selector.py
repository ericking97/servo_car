from servo_car.utils.node import Node


class ShiftSelector:
    """
    Simulates a car's gear shift selector using a doubly linked list of speed nodes.

    Gears are built from a list of integer speeds and sorted in ascending order,
    so shifting up always increases speed and shifting down always decreases it.
    Each gear is a Node in a doubly linked list, allowing O(1) traversal in
    either direction. The boundary nodes have no previous (lowest gear) or
    no next (highest gear), so attempting to shift past either end raises
    a ValueError.

    Attributes:
        current (Node): The currently selected gear node.
        gears (list[Node]): Ordered list of all gear nodes, from slowest to fastest.

    Example:
        >>> selector = ShiftSelector([30, 60, 90, 120])
        >>> selector.speed
        30
        >>> selector.shift_up()
        >>> selector.speed
        60
        >>> selector.shift_down()
        >>> selector.speed
        30
    """

    current: Node
    gears: list[Node]

    def __init__(self, speeds: list[int]):
        """
        Initialise the shift selector and set the starting gear to the slowest speed.

        The provided speeds do not need to be pre-sorted — they are sorted
        internally in ascending order before the linked list is built.

        :param speeds: A non-empty list of integer speed values representing
                       each available gear (e.g. [30, 60, 90, 120]).
        :raises ValueError: If ``speeds`` is empty.
        """
        self.gears = self._init_gears(speeds)
        self.current = self.gears[0]

    def _init_gears(self, speeds: list[int]) -> list[Node]:
        """
        Build a sorted doubly linked list of gear nodes from the given speeds.

        Speeds are sorted in ascending order so that shifting up always moves
        to a higher value. Each Node is linked to its predecessor and successor,
        except for the first node (no ``prev``) and the last node (no ``next``).

        :param speeds: A non-empty list of integer speed values.
        :returns: An ordered list of linked Node objects, from slowest to fastest.
        :raises ValueError: If ``speeds`` is empty.
        """
        if not speeds:
            raise ValueError("At least one speed is required")

        speeds.sort()
        gears: list[Node] = []

        for i, speed in enumerate(speeds):
            gear = Node(speed)

            if i > 0:
                prev_gear = gears[i - 1]
                gear.prev = prev_gear
                prev_gear.next = gear

            gears.append(gear)

        return gears

    @property
    def speed(self) -> int:
        """
        The speed value of the currently selected gear.

        :returns: An integer representing the current gear's speed.
        """
        return self.current.data

    def shift_up(self):
        """
        Advance to the next higher gear.

        Moves ``current`` to the next node in the linked list, which holds
        the next greater speed value. Has no side effects on the gear list itself.

        :raises ValueError: If the selector is already in the highest gear,
                            i.e. ``current.next`` is None.
        """
        if not self.current.next:
            raise ValueError(f"Already at the highest gear ({self.current.data})")
        self.current = self.current.next

    def shift_down(self):
        """
        Retreat to the next lower gear.

        Moves ``current`` to the previous node in the linked list, which holds
        the next smaller speed value. Has no side effects on the gear list itself.

        :raises ValueError: If the selector is already in the lowest gear,
                            i.e. ``current.prev`` is None.
        """
        if not self.current.prev:
            raise ValueError(f"Already at the lowest gear ({self.current.data})")
        self.current = self.current.prev

    def __repr__(self) -> str:
        """
        Return an unambiguous string representation of the selector's current state.

        Useful for debugging — shows all available gears and which one is active.

        :returns: A string in the form
                  ``ShiftSelector(gears=[30, 60, 90, 120], current=60)``.
        """
        gear_values = [node.data for node in self.gears]
        return f"ShiftSelector(gears={gear_values}, current={self.current.data})"
