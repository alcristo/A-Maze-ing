from numpy import zeros, ones, inf
from numpy.typing import NDArray
from typing import Any
from abc import ABC, abstractmethod
import sys
import random as rng


"""Maze generation module.

This module provides a MazeGenerator class for generating and displaying mazes.

Example:
    from mazegen import MazeGenerator


    generator = MazeGenerator(20, 20, '0,0', '19,19', seed=42)

    maze = generator.maze
    solution = generator.solution

Custom parameters:
    MazeGenerator(width=30, height=30, seed=123)

The generated maze can be accessed through ``maze`` and a solution
through ``solution``.
"""


def _get_walls(n: int) -> tuple[int, ...]:
    """Get the walls in a tile, return bit tuple.

    Arguments:
        n: The value of the tile.

    Raises:
        ValueError: If n is negative or higher than 15.
    """
    if n > 15 or n < 0:
        raise ValueError
    bits = []
    bits.append(n // 8)
    n %= 8
    bits.append(n // 4)
    n %= 4
    bits.append(n // 2)
    n %= 2
    bits.append(n)
    bits.reverse()
    return tuple(bits)


def _manhattan(curr: tuple[int, int], neigh: tuple[int, int]) -> int:
    """Manhattan heuristic, return distance."""
    return abs(curr[0] - neigh[0]) + abs(curr[1] - neigh[1])


class _Algorithm(ABC):
    """Abstract class for maze generation algorithms."""

    @abstractmethod
    def _generate(
        self, maze: NDArray[Any], seed: str | int | None = None
    ) -> None:
        """Generate the maze."""
        pass

    @staticmethod
    def _unvisited_set(visited: NDArray[Any]) -> set[tuple[int, int]]:
        """Return the unvisited tiles set from an array."""
        yet = set()
        for i in range(visited.shape[0]):
            for j in range(visited.shape[1]):
                if visited[i, j] == 0:
                    yet.add((i, j))
        return yet

    @staticmethod
    def _maze_init(
        maze: NDArray[Any], visited: NDArray[Any], seed: str | int | None
    ) -> tuple[int, int]:
        """Set first visited tile of the maze, return it as tuple."""
        h, w = maze.shape[:]
        v = -1
        rng.seed(seed)
        while v == -1:
            current = (rng.randrange(0, h - 1), rng.randrange(0, w - 1))
            v = visited[current[:]]
        visited[current[:]] = 1
        return current

    @staticmethod
    def _connect(
        maze: NDArray[Any], curr: tuple[int, int], neigh: tuple[int, int]
    ) -> None:
        """Connect two maze tiles."""
        if _manhattan(curr, neigh) != 1:
            return
        if curr[0] == neigh[0] + 1 and _get_walls(
            maze[curr[:]]
        )[0] == 1:
            maze[curr[0]][curr[1]] -= 1
            maze[neigh[0]][neigh[1]] -= 4
        if curr[0] == neigh[0] - 1 and _get_walls(
            maze[curr[:]]
        )[2] == 1:
            maze[curr[0]][curr[1]] -= 4
            maze[neigh[0]][neigh[1]] -= 1
        if curr[1] == neigh[1] - 1 and _get_walls(
            maze[curr[:]]
        )[1] == 1:
            maze[curr[0]][curr[1]] -= 2
            maze[neigh[0]][neigh[1]] -= 8
        if curr[1] == neigh[1] + 1 and _get_walls(
            maze[curr[:]]
        )[3] == 1:
            maze[curr[0]][curr[1]] -= 8
            maze[neigh[0]][neigh[1]] -= 2

    @staticmethod
    def _direction() -> tuple[str, int]:
        """Choose a direction, return tuple."""
        if rng.random() < .5:
            axis = "V"
        else:
            axis = "H"
        if rng.random() < .5:
            step = -1
        else:
            step = 1
        return (axis, step)

    def _gen_visited(self, maze: NDArray[Any]) -> None:
        """Generate auxiliar array to keep track of visited tiles."""
        visited = zeros(maze.shape, int)
        if visited.shape[0] > 6 and visited.shape[1] > 8:
            hs = (visited.shape[0] - 1) // 2 - 2
            ws = (visited.shape[1] - 1) // 2 - 3
            pos_42 = (
                (hs, ws), (hs + 1, ws), (hs + 2, ws), (hs + 2, ws + 1),
                (hs + 2, ws + 2), (hs + 3, ws + 2), (hs + 4, ws + 2),
                (hs, ws + 4), (hs, ws + 5), (hs, ws + 6),
                (hs + 1, ws + 6),
                (hs + 2, ws + 6), (hs + 2, ws + 5), (hs + 2, ws + 4),
                (hs + 3, ws + 4), (hs + 4, ws + 4), (hs + 4, ws + 5),
                (hs + 4, ws + 6)
            )
            for i in pos_42:
                visited[i[0]][i[1]] = -1
        self._visited = visited


class _DFS(_Algorithm):
    """Depth First Search / Recursive Backtracker algorithm private class."""

    def _generate(
        self, maze: NDArray[Any], seed: str | int | None = None
    ) -> None:
        """Depth First Search / Recursive Backtracker algorithm."""
        self._gen_visited(maze)
        visited = self._visited
        current = self._maze_init(maze, visited, seed)
        
        # The path to backtrack
        lst = [current]
        while len(lst) > 0:
            # Set with unvisited tiles
            nvis = set()
            h, w = current[:]
            neighs = ((h - 1, w), (h, w + 1), (h + 1, w), (h, w - 1))
            # Add unvisited neighbours to the set
            for i in neighs:
                try:
                    if True in [
                        i[j] in (-1, maze.shape[j]) for j in [0, 1]
                    ]:
                        raise IndexError
                    if visited[i[:]] == 0:
                        nvis.add(i[:])
                except IndexError:
                    continue
            if len(nvis) == 0:
                # If all neighbours are visited, backtrack the path
                lst.pop()
            else:
                # Connect one of the neighbours, keep track of the path
                new = rng.choice([*nvis])
                nvis.clear()
                self._connect(maze, current, new)
                visited[new[:]] = 1
                lst.append(new)
            try:
                current = lst[-1]
            except IndexError:
                pass


class _Prim(_Algorithm):
    """Prim's algorithm private class."""

    def _generate(
        self, maze: NDArray[Any], seed: str | int | None = None
    ) -> None:
        """Prim's algorithm."""
        self._gen_visited(maze)
        visited = self._visited
        rng.seed(seed)
        current = self._maze_init(maze, visited, seed)
        # Open set for tiles with neighbours
        opened: set[tuple[int, int]] = set()
        opened.add(current)
        while len(opened) > 0:
            # Set of unvisited neighbours
            nvis = set()
            h, w = current[:]
            neighs = ((h - 1, w), (h, w + 1), (h + 1, w), (h, w - 1))
            # Check for unvisited neighbours
            for i in neighs:
                try:
                    if True in [
                        i[j] in (-1, maze.shape[j]) for j in [0, 1]
                    ]:
                        raise IndexError
                    if visited[i[:]] == 0:
                        nvis.add(i[:])
                except IndexError:
                    continue
            if len(nvis) == 0:
                # If no neighbours to visit, remove tile from open set
                opened.remove(current)
            else:
                # Connect tiles, add neighbour to open set
                new = rng.choice([*nvis])
                nvis.clear()
                self._connect(maze, current, new)
                visited[new[:]] = 1
                opened.add(new)
            if len(opened) > 0:
                # Choose a random tile from the open set
                current = tuple[int, int](rng.choice([*opened]))


class _Wilson(_Algorithm):
    """Wilson's algorithm private class."""

    @staticmethod
    def _wilson_erase(
        visited: NDArray[Any],
        path: list[tuple[int, int]],
        point: tuple[int, int]
    ) -> None:
        """Erase a loop during random walk."""
        while path[-1] != point:
            visited[path[-1][:]] = 0
            path.pop()

    def _generate(
        self, maze: NDArray[Any], seed: str | int | None = None
    ) -> None:
        """Wilson's algorithm."""
        self._gen_visited(maze)
        visited = self._visited
        current = self._maze_init(maze, visited, seed)
        yet = self._unvisited_set(visited)
        while len(yet) > 0:
            # Initialize path, choose a random unvisited tile
            path = []
            current = rng.choice([*yet])
            visited[current[0], current[1]] = 2
            path.append(current)
            while current in yet:
                # Choose a direction to move
                direct = self._direction()
                try:
                    if direct[0] == "V":
                        # Vertical movement
                        if current[0] + direct[1] in (-1, maze.shape[0]):
                            raise IndexError
                        neighbour = (current[0] + direct[1], current[1])
                    else:
                        # Horizontal movement
                        if current[1] + direct[1] in (-1, maze.shape[1]):
                            raise IndexError
                        neighbour = (current[0], current[1] + direct[1])
                except IndexError:
                    continue
                if visited[neighbour[0], neighbour[1]] == -1:
                    # Moves to forbidden tile (42)
                    continue
                elif visited[neighbour[0], neighbour[1]] == 1:
                    # Moves to the maze
                    path.append(neighbour)
                    break
                elif neighbour in path:
                    # Moves to the path itself: loop erase random walk
                    self._wilson_erase(visited, path, neighbour)
                # Random walk
                current = neighbour
                visited[current[0], current[1]] = 2
                if current not in path:
                    path.append(current)
            for tile in path:
                # After exit remove path tiles from set
                visited[tile[0], tile[1]] = 1
                yet.discard(tile)
            while len(path) > 1:
                # Connect tiles following the path
                self._connect(maze, path[-2], path[-1])
                current = path[-1]
                path.pop()
            path.clear()


class _AldousBroder(_Algorithm):
    """Aldous-Broder algorithm private class."""

    def _generate(
        self, maze: NDArray[Any], seed: str | int | None = None
    ) -> None:
        """Aldous-Broder algorithm."""
        self._gen_visited(maze)
        visited = self._visited
        rng.seed(seed)
        current = self._maze_init(maze, visited, seed)
        yet = self._unvisited_set(visited)
        while len(yet) > 0:
            # Random walk
            direct = self._direction()
            try:
                if direct[0] == "V":
                    neighbour = (current[0] + direct[1], current[1])
                    if current[0] + direct[1] in (-1, maze.shape[0]):
                        raise IndexError
                else:
                    neighbour = (current[0], current[1] + direct[1])
                    if current[1] + direct[1] in (-1, maze.shape[1]):
                        raise IndexError
            except IndexError:
                continue
            if visited[neighbour[0], neighbour[1]] == -1:
                # Moves to forbidden tile (42)
                continue
            elif visited[neighbour[0], neighbour[1]] == 0:
                # Moves to unvisited tile, connects tiles
                self._connect(maze, current, neighbour)
                yet.discard(neighbour)
            current = neighbour
            visited[current[0], current[1]] = 1


class _Imperfect(_Algorithm):
    """Algorithm class for imperfect mazes."""

    def _break_wall(
        self, maze: NDArray[Any], tile: tuple[int, int], op: str
    ) -> None:
        """Connect the chosen tiles."""
        i, j = tile[:]
        if op == "N":
            self._connect(maze, tile, (i - 1, j))
        elif op == "E":
            self._connect(maze, tile, (i, j + 1))
        elif op == "S":
            self._connect(maze, tile, (i + 1, j))
        elif op == "W":
            self._connect(maze, tile, (i, j - 1))

    def _remove_walls(
        self, maze: NDArray[Any], tile: tuple[int, int], prob: float = 1
    ) -> None:
        """Check for neighbouring removable walls."""
        if maze[tile[:]] == 15 or prob < 0 or prob > 1:
            return
        i, j = tile[:]
        walls = _get_walls(maze[tile[:]])
        r_walls = []
        if i > 0:
            if maze[i - 1][j] != 15 and walls[0] == 1:
                r_walls.append("N")
        if j < maze.shape[1] - 1:
            if maze[i][j + 1] != 15 and walls[1] == 1:
                r_walls.append("E")
        if i < maze.shape[0] - 1:
            if maze[i + 1][j] != 15 and walls[2] == 1:
                r_walls.append("S")
        if j > 0:
            if maze[i][j - 1] != 15 and walls[3] == 1:
                r_walls.append("W")
        if len(r_walls) > 0 and rng.random() < prob:
            self._break_wall(maze, tile, rng.choice(r_walls))

    def _generate(
        self, maze: NDArray[Any], seed: str | int | None = None
    ) -> None:
        """Algorithm for braiding perfect mazes."""

        h, w = maze.shape

        # If maze is just a line, stop
        if 1 in (h, w):
            return

        # Start _connecting the four corners
        self._connect(maze, (0, 0), (0, 1))
        self._connect(maze, (0, 0), (1, 0))
        self._connect(maze, (0, w - 1), (0, w - 2))
        self._connect(maze, (0, w - 1), (1, w - 1))
        self._connect(maze, (h - 1, w - 1), (h - 1, w - 2))
        self._connect(maze, (h - 1, w - 1), (h - 2, w - 1))
        self._connect(maze, (h - 1, 0), (h - 1, 1))
        self._connect(maze, (h - 1, 0), (h - 2, 0))

        # Remove random walls in random tiles
        for _ in range(h * w // 3):
            tile = (rng.randrange(h), rng.randrange(w))
            self._remove_walls(maze, tile, .5)
        dead_ends = (7, 11, 13, 14)
        s_wall = ((0, 1), (0, 2), (0, 4), (0, 8))
        adm_walls = [1, 2, 3, 4, 5, 6, 8, 9, 10, 12]

        # Remove dead ends; ignores 42
        for i in range(h):
            for j in range(w):
                if maze[i, j] in dead_ends:
                    self._remove_walls(maze, (i, j))

        # Check for areas > 3x3; fill them in such case
        for i in range(h):
            for j in range(w):
                if maze[i, j] == 0:
                    adj_tiles = [
                        (i - 1, j),
                        (i, j + 1),
                        (i + 1, j),
                        (i, j - 1)
                    ]
                    adj_walls = [
                        maze[
                            adj_tiles[k][:]
                        ] in s_wall[k] for k in range(len(adj_tiles))
                    ]
                    if False not in adj_walls:
                        maze[i, j] = rng.choice(adm_walls)
                        walls = _get_walls(maze[i, j])
                        if walls[0] == 1:
                            maze[i - 1][j] += 4
                        if walls[1] == 1:
                            maze[i][j + 1] += 8
                        if walls[2] == 1:
                            maze[i + 1][j] += 1
                        if walls[3] == 1:
                            maze[i][j - 1] += 2


class _Maze:
    """Private class for the maze."""

    def __init__(
        self,
        height: int,
        width: int,
        perfect: bool,
        seed: int | str | None = None,
        algorithm: str = "Prim"
    ) -> None:
        """Initialize a maze.

        Arguments:
            height: The maze height. Must be positive.
            width: The maze width. Must be positive.
            perfect: Whether the maze is perfect or not.

        Keyword arguments:
            seed: The seed for the mazer generation (default None).
            algorithm: The maze generation algorithm. (default 'Prim').
        """
        self._height = height
        self._width = width
        self._perfect = perfect
        self._seed = seed
        if algorithm.lower() in (
            "dfs", "recursive backtracker", "depth first search"
        ):
            self._algo: _Algorithm = _DFS()
        elif algorithm.lower() == "prim":
            self._algo = _Prim()
        elif algorithm.lower() in (
            "ab", "aldous broder", "aldous-broder"
        ):
            self._algo = _AldousBroder()
        elif algorithm.lower() == "wilson":
            self._algo = _Wilson()
        else:
            print("[ERROR] Invalid algorithm", file=sys.stderr)
            return

    def __str__(self) -> str:
        """Print the maze as a hexadecimal grid.

        Bits represent the wall status (0 open; 1 closed):
            0: N
            1: E
            2: S
            3: W
        """
        base = "0123456789abcdef"
        s = ""
        for i in range(self._maze.shape[0]):
            for j in range(self._maze.shape[1]):
                try:
                    if self._maze[i, j] >= 0 and self._maze[i, j] < 16:
                        s += base[self._maze[i][j]]
                    else:
                        print(f"({i}, {j}): {self._maze[i, j]}")
                        raise IndexError
                except IndexError:
                    print("\r[ERROR] Maze can't be displayed", file=sys.stderr)
                    sys.exit(1)
            s += "\n"
        return s

    def _generate(self) -> None:
        """Generate the maze."""
        self._maze = 15 * ones([self._height, self._width], int)
        self._algo._generate(self._maze, self._seed)
        if self._perfect is False:
            imp = _Imperfect()
            imp._generate(self._maze, self._seed)

    @property
    def height(self) -> int:
        return self._height

    @property
    def width(self) -> int:
        return self._width

    @property
    def perfect(self) -> bool:
        return self._perfect

    @property
    def seed(self) -> str | int | None:
        return self._seed

    @property
    def algorithm(self) -> _Algorithm:
        return self._algo

    @property
    def maze(self) -> NDArray[Any]:
        return self._maze


class _Node:
    """Private class for the path nodes."""

    def __init__(self, value: Any) -> None:
        """Initialize a node.

        Arguments:
            val: The value. For this project, a tuple representing a tile.

        Additional variables:
            g: the distance from the node to the entrance.
            h: the ideal distance from the node to the exit.
            f: the sum of g + h.
            next: The next node.
        """
        self.val = value
        self._g = inf
        self._h = inf
        self._f = inf
        self.next: Any = None

    def _size(self) -> int:
        """Get the length of the node chain."""
        first = self
        n = 1
        while self.next is not None and self.next is not first:
            n += 1
            self = self.next
        return n

    def _get_g(self) -> int | float:
        return self._g

    def _get_h(self) -> int | float:
        return self._h

    def _get_f(self) -> int | float:
        return self._f

    def _set_f(self, f: int | float) -> None:
        self._f = f

    def _set_g(self, g: int | float) -> None:
        self._g = g
        self._set_f(self._get_g() + self._get_h())

    def _set_h(self, h: int | float) -> None:
        self._h = h
        self._set_f(self._get_g() + self._get_h())


class _Path:
    """Private class to store the solution. """

    def __init__(
        self,
        maze: NDArray[Any],
        entry: tuple[int, int],
        exit: tuple[int, int]
    ) -> None:
        """Initialize a path.

        Arguments:
            maze: The maze as a Numpy array.
            entry: The maze entry.
            exit: The maze exit."""
        self._entry = entry
        self._exit = exit
        self._maze = maze
        self._path = ""
        self._checked = 0

    def __str__(self) -> str:
        """Print path from entry to exit in cardinal directions."""
        return self._path

    @staticmethod
    def _neighbours(
        maze: NDArray[Any], current: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """Return reachable neighbours list from a maze tile."""
        n = maze[current[:]]
        neighs = []
        walls = _get_walls(n)
        if walls[0] == 0:
            neighs.append((current[0] - 1, current[1]))
        if walls[1] == 0:
            neighs.append((current[0], current[1] + 1))
        if walls[2] == 0:
            neighs.append((current[0] + 1, current[1]))
        if walls[3] == 0:
            neighs.append((current[0], current[1] - 1))
        return neighs

    @staticmethod
    def _choose_current(
        f: NDArray[Any], points: list[_Node], exit: tuple[int, int]
    ) -> _Node:
        """Return most promising node to evaluate."""
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
            h = _manhattan(k.val, exit)
            if h < min_h:
                min_h = h
                current = k
        return current

    @staticmethod
    def _check_node(set: set[_Node], point: tuple[int, int]) -> bool:
        """Check point coordinates in a set return bool.

        Arguments:
            set: A set of nodes.
            point: a maze coordinate
        """
        for i in set:
            if i.val == point:
                return True
        return False

    @staticmethod
    def _rm_node(
        set: set[_Node], new: _Node
    ) -> None:
        """Remove a node from a set."""
        alt_path = []
        for n in set:
            if n.val == new.val:
                alt_path.append(n)

        for n in alt_path:
            if new._get_g() < n._get_g():
                set.remove(n)
        if len(alt_path) == 0:
            set.add(new)

    @staticmethod
    def _add_front(old: _Node, newnode: _Node) -> None:
        """Add a new node pointing to the old node."""
        if newnode is None:
            return
        newnode.next = old

    def _solve(self) -> None:
        """A* pathfinding algorithm with Manhattan heuristic."""

        opened, closed = set(), set()
        g_cost = inf * ones(self._maze.shape[:], int)
        f_cost = inf * ones(self._maze.shape[:], int)
        opened.add(_Node(self._entry))
        f_cost[self._entry[:]] = _manhattan(self._entry, self._exit)
        g_cost[self._entry[:]] = 0
        self._checked = 0
        while len(opened) > 0:
            self._checked += 1

            # Choose current node, move from open list to closed list
            current = self._choose_current(f_cost, list(opened), self._exit)
            opened.remove(current)
            closed.add(current)

            # If node is the exit, path has been found
            if current.val == self._exit:
                break
            for i in self._neighbours(self._maze, current.val):

                # If node is already closed, continue
                if self._check_node(closed, i) is True:
                    continue
                node = _Node(i)
                self._add_front(current, node)
                node._set_g(node._size() - 1)

                # Check the route to the node is "cheaper"
                if node._get_g() < g_cost[i[:]]:
                    g_cost[i[:]] = node._get_g()
                    self._rm_node(opened, node)
                else:
                    continue
                node._set_h(_manhattan(i, self._exit))

                # Update F cost if is lower
                if node._get_f() < f_cost[i[:]] or self._check_node(
                    opened, i
                ) is False:
                    f_cost[i[:]] = node._get_f()
                    if self._check_node(opened, i) is False:
                        opened.add(node)

        # Return the maze solution via backtracking
        while current.next is not None:
            if current.val[0] == current.next.val[0] + 1:
                self._path = "S" + self._path
            elif current.val[0] == current.next.val[0] - 1:
                self._path = "N" + self._path
            elif current.val[1] == current.next.val[1] + 1:
                self._path = "E" + self._path
            elif current.val[1] == current.next.val[1] - 1:
                self._path = "W" + self._path
            current = current.next

    @property
    def checked(self) -> int:
        return self._checked

    @property
    def path(self) -> str:
        return self._path


class MazeGenerator:
    """Class for generating and displaying mazes."""

    def __init__(
        self,
        height: int,
        width: int,
        start: str,
        end: str,
        perfect: bool = False,
        seed: str | None = None,
        algorithm: str = "Prim"
    ) -> None:
        """Initialize a maze generator.

        Arguments:
            height: Height of the maze.
            width: Width of the maze.
            start: Entry of the maze.
            end: Exit of the maze.

        Keyword arguments:
            perfect: Whether the maze is perfect (default False).
            seed: Optional random seed.
            algorithm: The generation algorithm. Accepts DFS, Prim (default),
            Wilson and Aldous-Broder."""
        try:
            assert height > 0
            assert width > 0
            self._height = height
            self._width = width
            en = start.split(",")
            self._entry = (int(en[1]), int(en[0]))
            ex = end.split(",")
            self._exit = (int(ex[1]), int(ex[0]))
            self._perfect = perfect
            self._seed = seed
            self._algorithm = algorithm
            self._gen = True
            try:
                self._valid_entry_exit()
            except ValueError:
                self._gen = False
            self._palette: dict[str, str] = {}
            self.regen()
        except AssertionError:
            print("[ERROR] Maze dimensions must be positive", file=sys.stderr)
            self._gen = False
        except ValueError as e:
            print(f"[ERROR] Configuration in wrong format: {e}")
            self._gen = False
        except IndexError:
            print("[ERROR] Entry/Exit in wrong format. Usage ex.: EXIT=0,0")
            self._gen = False

    def _valid_entry_exit(self) -> None:
        """Check entry and exit are valid.

        Raises:
            ValueError: if:
                Entry and exit are equal.
                Entry or exit are out of maze bounds.
                Entry or exit will be in unreachable tiles.
        """

        # Check entry and exit are not equal
        if self._entry == self._exit:
            print("[ERROR] Entry and exit must not be equal", file=sys.stderr)
            raise ValueError

        size = (self._height, self._width)
        # Check entry or exit are not out of bounds
        en = (
            self._entry[0] < 0 or self._entry[0] >= size[0],
            self._entry[1] < 0 or self._entry[1] >= size[1]
        )
        if True in en:
            print("[ERROR] Entry is out of bounds", file=sys.stderr)
            raise ValueError
        ex = (
            self._exit[0] < 0 or self._exit[0] >= size[0],
            self._exit[1] < 0 or self._exit[1] >= size[1]
        )
        if True in ex:
            print("[ERROR] Exit is out of bounds", file=sys.stderr)
            raise ValueError

        # Check entry or exit are not inside the 42
        if size[0] < 7 or size[1] < 9:
            print("The '42' cannot be printed in a maze this size.")
        else:
            hs, ws = (size[0] - 1) // 2 - 2, (size[1] - 1) // 2 - 3
            pos_42 = (
                (hs, ws), (hs + 1, ws), (hs + 2, ws), (hs + 2, ws + 1),
                (hs + 2, ws + 2), (hs + 3, ws + 2), (hs + 4, ws + 2),
                (hs, ws + 4), (hs, ws + 5), (hs, ws + 6), (hs + 1, ws + 6),
                (hs + 2, ws + 6), (hs + 2, ws + 5), (hs + 2, ws + 4),
                (hs + 3, ws + 4), (hs + 4, ws + 4), (hs + 4, ws + 5),
                (hs + 4, ws + 6)
            )
            if self._entry in pos_42:
                print("[ERROR] Entry is inside '42'", file=sys.stderr)
                raise ValueError
            if self._exit in pos_42:
                print("[ERROR] Exit is inside '42'", file=sys.stderr)
                raise ValueError

    def _generate(self) -> None:
        """Generate the maze."""
        self._maze = _Maze(
            self._height,
            self._width,
            self._perfect,
            self._seed,
            self._algorithm
        )
        try:
            if self._gen is True:
                self._maze._generate()
        except AttributeError:
            return

    def _solve(self) -> None:
        """Solve the maze."""
        try:
            self._path = _Path(self._maze._maze, self._entry, self._exit)
            self._path._solve()
        except AttributeError:
            print("[ERROR] No maze to solve", file=sys.stderr)

    def color(self, key: str, color: list[int] = []) -> None:
        """Change the color of a palette.

        Arguments:
            key: Part of the maze to paint.
                Accepts "tile", "wall", "entry", "exit", "path" and "block".
            color: List of three uint8 numbers.
                If not valid, removes the key from the palette.
        """
        valid_keys = ("tile", "wall", "entry", "exit", "path", "block")
        if key.lower() not in valid_keys:
            return
        if len(color) != 3:
            if self._palette.get(key) is not None:
                self._palette.pop(key)
            return
        valid_colors = [i >= 0 and i <= 255 for i in color]
        if False in valid_colors:
            if self._palette.get(key) is not None:
                self._palette.pop(key)
            return
        self._palette.update(
            {key.lower(): f"\x1b[48;2;{color[0]};{color[1]};{color[2]}m"}
            )

    def draw(self, solution: bool = False) -> None:
        """Draw the maze.

        Arguments:
            solution: whether the solution has to be drawn (default False).

        If a palette key is missing, a default color for it is used.
        """
        pathtiles = []
        curr = self._entry
        if solution is True:
            for dir in self._path._path:
                if dir == "N":
                    curr = (curr[0] - 1, curr[1])
                elif dir == "S":
                    curr = (curr[0] + 1, curr[1])
                elif dir == "W":
                    curr = (curr[0], curr[1] - 1)
                elif dir == "E":
                    curr = (curr[0], curr[1] + 1)
                else:
                    break
                if curr == self._exit:
                    break
                pathtiles.append(curr)
            pathtiles.append(self._exit)
            pathtiles.insert(0, self._entry)

        reset = "\x1b[0m"
        tile = self._palette.get("tile", "\x1b[47m")
        wall = self._palette.get("wall", "\x1b[40m")
        entry = self._palette.get("entry", "\x1b[45m")
        exit = self._palette.get("exit", "\x1b[42m")
        path = self._palette.get("path", "\x1b[44m")
        block = self._palette.get("block", "\x1b[41m")

        # Top wall
        h, w = self._maze._maze.shape
        for _ in range(2 * w + 1):
            print(f"{wall}  {reset}", end="")
        print()
        i = 0
        for i in range(h):
            print(f"{wall}  {reset}", end="")
            # Row with horizontal connections
            for j in range(w):
                n = self._maze._maze[i, j]
                if n == 15:
                    print(f"{block}  {reset}", end="")
                elif (i, j) == self._entry:
                    print(f"{entry}  {reset}", end="")
                elif (i, j) == self._exit:
                    print(f"{exit}  {reset}", end="")
                elif (i, j) in pathtiles:
                    print(f"{path}  {reset}", end="")
                else:
                    print(f"{tile}  {reset}", end="")
                if (i, j) in pathtiles and (
                    i, j + 1
                ) in pathtiles and _get_walls(n)[1] == 0:
                    print(f"{path}  {reset}", end="")
                elif _get_walls(n)[1] == 0:
                    print(f"{tile}  {reset}", end="")
                else:
                    print(f"{wall}  {reset}", end="")
            print()

            # Row with vertical connections
            print(f"{wall}  {reset}", end="")
            for j in range(w):
                n = self._maze._maze[i, j]
                if (i, j) in pathtiles and (
                    i + 1, j
                ) in pathtiles and _get_walls(n)[2] == 0:
                    print(f"{path}  {reset}", end="")
                elif _get_walls(n)[2] == 0:
                    print(f"{tile}  {reset}", end="")
                else:
                    print(f"{wall}  {reset}", end="")

                # Do not paint isolated (single-pixel) walls
                if i != range(h)[-1] and j != range(w)[-1]:
                    p_path = [
                        _get_walls(n)[1] == 0,
                        _get_walls(n)[2] == 0,
                        _get_walls(self._maze._maze[i + 1][j])[0] == 0,
                        _get_walls(self._maze._maze[i + 1][j])[1] == 0,
                        _get_walls(self._maze._maze[i][j + 1])[2] == 0,
                        _get_walls(self._maze._maze[i][j + 1])[3] == 0
                    ]
                    if False not in p_path:
                        print(f"{tile}  {reset}", end="")
                    else:
                        print(f"{wall}  {reset}", end="")
                else:
                    print(f"{wall}  {reset}", end="")
            print()

    def output(self, filename: str) -> None:
        """Save the maze in an output file."""
        base = "0123456789abcdef"
        try:
            self._maze
        except AttributeError:
            print("[ERROR] No maze to print", file=sys.stderr)
            return
        with open(filename, 'w') as out:
            for i in range(self._maze.height):
                for j in range(self._maze.width):
                    out.write(base[self._maze._maze[i, j]])
                out.write("\n")
            out.write("\n")
            out.write(f"{self._entry[1]},{self._entry[0]}\n")
            out.write(f"{self._exit[1]},{self._exit[0]}\n")
            out.write(self._path._path)

    def regen(self) -> None:
        """Regenerate and solve the maze."""
        try:
            self._generate()
            self._solve()
        except AttributeError:
            return

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, h: int) -> None:
        if h <= 0:
            print("[ERROR] Height must be positive")
            return
        self._height = h
        if h < 7:
            print("The '42' cannot be printed in a maze this size.")
        try:
            self._valid_entry_exit()
        except ValueError:
            self._gen = False
        else:
            self._gen = True

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, w: int) -> None:
        if w <= 0:
            print("[ERROR] Width must be positive")
            return
        self._width = w
        if w < 9:
            print("The '42' cannot be printed in a maze this size.")
        try:
            self._valid_entry_exit()
        except ValueError:
            self._gen = False
        else:
            self._gen = True

    @property
    def entry(self) -> tuple[int, int]:
        return self._entry

    @entry.setter
    def entry(self, en: tuple[int, int]) -> None:
        self._entry = (en[1], en[0])
        try:
            self._valid_entry_exit()
        except ValueError:
            self._gen = False
        else:
            self._gen = True

    @property
    def exit(self) -> tuple[int, int]:
        return self._exit

    @exit.setter
    def exit(self, ex: tuple[int, int]) -> None:
        self._exit = (ex[1], ex[0])
        try:
            self._valid_entry_exit()
        except ValueError:
            self._gen = False
        else:
            self._gen = True

    @property
    def perfect(self) -> bool:
        return self._perfect

    @perfect.setter
    def perfect(self, p: bool) -> None:
        self._perfect = p

    @property
    def seed(self) -> str | None:
        return self._seed

    @seed.setter
    def seed(self, s: str | None) -> None:
        self._seed = s

    @property
    def algorithm(self) -> str:
        return self._algorithm

    @algorithm.setter
    def algorithm(self, algo: str) -> None:
        valid_algos = (
            "wilson", "prim", "dfs", "ab", "aldous broder", "aldousbroder",
            "aldous_broder", "aldous-broder", "depth first search",
            "depthfirstserach", "depth_first_search", "recursivebacktracker",
            "recursive backtracker", "recursive_backtracker", "rb"
        )
        if algo.lower() in valid_algos:
            self._algorithm = algo

    @property
    def maze(self) -> _Maze:
        return self._maze

    @property
    def path(self) -> _Path:
        return self._path

    @property
    def solution(self) -> str:
        return self._path.path

    @property
    def palette(self) -> dict[str, str]:
        return self._palette
