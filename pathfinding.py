from numpy.typing import NDArray
from numpy import Inf
from .maze_utils import get_walls, manhattan


"""Node class to track down the path"""
class Node():
    def __init__(self, value):
        self.val = value
        self.next = None

    def add_front(self, newnode):
        if newnode is None:
            return
        newnode.next = self
        self = newnode


"""Return reachable neighbours list from a maze tile"""
def neighbours(maze: NDArray, current: tuple[int]) -> list[tuple]:
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


"""Return most promising point to evaluate"""
def choose_current(f: NDArray, points: list[Node], exit: tuple[int]) -> Node:
    n = Inf
    f_cost = []
    for i in points:
        p = i.val
        f_cost.append(f[p[:]])
    min_f = min(f_cost)
    to_select = []
    for j in range(len(f_cost)):
        if f_cost[j] == min_f:
            to_select.append(points[j])
    min_h = Inf
    for k in to_select:
        h = manhattan(k.val, exit)
        if h < min_h:
            min_h = h
            current = k
    return current


"""Check point in closed list"""
def check_closed(closed: list[Node], point: tuple[int]) -> bool:
    for i in closed:
        if i.val == point:
            return True
    return False


"""A* pathfinding algorithm with Manhattan heuristic"""
def a_star(maze: NDArray) -> str:
    """Initialize lists and F cost array"""
    opened, closed = [], []
    f_cost = Inf * ones(maze.shape[:], int)
    opened.append(Node(entr))
    f_cost[entr[:]] = manhattan(entr, exit)
    while len(opened) > 0:
        """Choose current node, move from open list to closed list"""
        current = choose_current(f_cost, opened, exit)
        opened.remove(current)
        closed.append(current)
        """If node is the exit, path has been found"""
        if current.val == exit:
            break
        for i in neighbours(maze, current.val):
            """If node is already closed, continue"""
            if check_closed(closed, i) is True:
                continue
            node = Node(i)
            node.next = current
            g = manhattan(i, entr)
            h = manhattan(i, exit)
            f = g - h
            """Update F cost if is lower"""
            if f < f_cost[i[:]]:
                f_cost[i[:]] = f
                if i in opened:
                    if manhattan(open[open.index(i)], entr) > g:
                        continue
                opened.append(node)
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
    print(len(closed))
    print(sol)