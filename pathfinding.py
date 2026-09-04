from numpy.typing import NDArray
from numpy import inf, ones
from typing import Any
from maze_utils import get_walls, manhattan


class Node:
    """Node class to track down the path"""

    def __init__(self, value: Any) -> None:
        self.val = value
        self._g: float | int = inf
        self._h: float | int = inf
        self._f: float | int = inf
        self.next: Any = None

    def size(self) -> int:
        """Return number of nodes connecting attached to the node."""
        first = self
        n = 1
        while self.next is not None and self.next is not first:
            n += 1
            self = self.next
        return n

    def get_g(self) -> int | float:
        return self._g

    def get_h(self) -> int | float:
        return self._h

    def get_f(self) -> int | float:
        return self._f

    def _set_f(self, f: int | float) -> None:
        self._f = f

    def set_g(self, g: int | float) -> None:
        self._g = g
        self._set_f(self.get_g() + self.get_h())

    def set_h(self, h: int | float) -> None:
        self._h = h
        self._set_f(self.get_g() + self.get_h())


def neighbours(
    maze: NDArray[Any], current: tuple[int, int]
) -> list[tuple[int, int]]:
    """Return reachable neighbours list from a maze tile."""
    n = maze[current[:]]
    neighs = []
    walls = get_walls(n)
    if walls[0] == 0:
        neighs.append((current[0] - 1, current[1]))
    if walls[1] == 0:
        neighs.append((current[0], current[1] + 1))
    if walls[2] == 0:
        neighs.append((current[0] + 1, current[1]))
    if walls[3] == 0:
        neighs.append((current[0], current[1] - 1))
    return neighs


def choose_current(
        f: NDArray[Any], points: list[Node], exit: tuple[int, int]
) -> Node:
    """Return most promising point to evaluate."""
    f_cost = []
    for i in points:
        p = i.val
        if p == exit:
            return i
        f_cost.append(f[p[:]])
    min_f = min(f_cost)
    to_select = []
    for j in range(len(f_cost)):
        if f_cost[j] == min_f:
            to_select.append(points[j])
    min_h = inf
    for k in to_select:
        h = manhattan(k.val, exit)
        if h < min_h:
            min_h = h
            current = k
    return current


def check_node(set: set[Node], point: tuple[int, int]) -> bool:
    """Check point in a set, return bool."""
    for i in set:
        if i.val == point:
            return True
    return False


def rm_node(set: set[Node], new: Node) -> None:
    """Remove node from set and add new one if shorter."""
    alt_path: list[Node] = []
    for n in set:
        if n.val == new.val:
            alt_path.append(n)

    for n in alt_path:
        if new.get_g() < n.get_g():
            set.remove(n)
    if len(alt_path) == 0:
        set.add(new)


def add_front(current: Node, new: Node) -> None:
    """Add a new node to the current head."""
    if new is None:
        return
    new.next = current


def a_star(
    maze: NDArray[Any], entr: tuple[int, int], exit: tuple[int, int]
) -> str:
    """A* pathfinding algorithm with Manhattan heuristic."""

    # Initialize lists and F cost array
    opened: set[Node] = set()
    closed: set[Node] = set()
    g_cost = inf * ones(maze.shape[:], int)
    f_cost = inf * ones(maze.shape[:], int)
    opened.add(Node(entr))
    f_cost[entr[:]] = manhattan(entr, exit)
    g_cost[entr[:]] = 0
    n = 0
    while len(opened) > 0:
        n += 1
        # Choose current node, move from open list to closed list
        current = choose_current(f_cost, list(opened), exit)
        opened.remove(current)
        closed.add(current)
        # If node is the exit, path has been found
        if current.val == exit:
            break
        for i in neighbours(maze, current.val):
            # If node is already closed, continue
            if check_node(closed, i) is True:
                continue
            node = Node(i)
            add_front(current, node)
            node.set_g(node.size() - 1)
            if node.get_g() < g_cost[i[:]]:
                g_cost[i[:]] = node.get_g()
                rm_node(opened, node)
            else:
                continue
            node.set_h(manhattan(i, exit))
            # Update F cost if is lower
            if node.get_f() < f_cost[i[:]] or check_node(opened, i) is False:
                f_cost[i[:]] = node.get_f()
                if check_node(opened, i) is False:
                    opened.add(node)

    # Return the maze solution via backtracking
    sol = ""
    while current.next is not None:
        if current.val[0] == current.next.val[0] + 1:
            sol = "S" + sol
        elif current.val[0] == current.next.val[0] - 1:
            sol = "N" + sol
        elif current.val[1] == current.next.val[1] + 1:
            sol = "E" + sol
        elif current.val[1] == current.next.val[1] - 1:
            sol = "W" + sol
        current = current.next
    return sol
