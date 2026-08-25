from numpy import zeros, ones, inf
from numpy.typing import NDArray
from abc import ABC, abstractmethod
import random as rng


class _Algorithm(ABC):

    @abstractmethod
    def generate(self, maze: NDArray):
        pass

    @staticmethod
    def unvisited_set(visited: NDArray) -> set:
        """Make the unvisited tiles set"""
        yet = set()
        for i in range(visited.shape[0]):
            for j in range(visited.shape[1]):
                if visited[i, j] == 0:
                    yet.add((i, j))
        return yet

    @staticmethod
    def maze_init(maze: NDArray, visited: NDArray) -> tuple[int, int]:
        h, w = maze.shape[:]
        v = -1
        while v == -1:
            current = (
                rng.randrange(0, h - 1), rng.randrange(0, w - 1)
            )
            v = visited[current[:]]
        visited[current[:]] = 1
        return current

    @staticmethod
    def connect(
        maze: NDArray, curr: tuple[int, int], neigh: tuple[int, int]
    ) -> None:
        """Connect two maze tiles"""
        if _Maze.manhattan(curr, neigh) != 1:
            return
        if curr[0] == neigh[0] + 1 and _Maze.get_walls(
            maze[curr[:]]
        )[0] == 1:
            maze[curr[0]][curr[1]] -= 1
            maze[neigh[0]][neigh[1]] -= 4
        if curr[0] == neigh[0] - 1 and _Maze.get_walls(
            maze[curr[:]]
        )[2] == 1:
            maze[curr[0]][curr[1]] -= 4
            maze[neigh[0]][neigh[1]] -= 1
        if curr[1] == neigh[1] - 1 and _Maze.get_walls(
            maze[curr[:]]
        )[1] == 1:
            maze[curr[0]][curr[1]] -= 2
            maze[neigh[0]][neigh[1]] -= 8
        if curr[1] == neigh[1] + 1 and _Maze.get_walls(
            maze[curr[:]]
        )[3] == 1:
            maze[curr[0]][curr[1]] -= 8
            maze[neigh[0]][neigh[1]] -= 2

    @staticmethod
    def direction() -> tuple[str, int]:
        """Choose a direction, return tuple"""
        if rng.random() < .5:
            axis = "V"
        else:
            axis = "H"
        if rng.random() < .5:
            step = -1
        else:
            step = 1
        return (axis, step)

    def gen_visited(self, maze: NDArray) -> None:
        visited = zeros(maze.shape, int)
        if visited.shape[0] < 6 or visited.shape[1] < 8:
            print("The '42' cannot be printed in a maze this size.")
        else:
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
    def generate(self, maze: NDArray):
        self.gen_visited(maze)
        visited = self._visited
        current = self.maze_init(maze, visited)
        lst = [current]
        while len(lst) > 0:
            nvis = set()
            h, w = current[:]
            neighs = ((h - 1, w), (h, w + 1), (h + 1, w), (h, w - 1))
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
                lst.pop()
            else:
                new = rng.choice([*nvis])
                nvis.clear()
                self.connect(maze, current, new)
                visited[new[:]] = 1
                lst.append(new)
            try:
                current = lst[-1]
            except IndexError:
                pass


class _Prim(_Algorithm):

    def generate(self, maze: NDArray):
        self.gen_visited(maze)
        visited = self._visited
        current = self.maze_init(maze, visited)
        opened: set[tuple[int, int]] = set()
        opened.add(current)
        while len(opened) > 0:
            nvis = set()
            h, w = current[:]
            neighs = ((h - 1, w), (h, w + 1), (h + 1, w), (h, w - 1))
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
                opened.remove(current)
            else:
                new = rng.choice([*nvis])
                nvis.clear()
                self.connect(maze, current, new)
                visited[new[:]] = 1
                opened.add(new)
            if len(opened) > 0:
                current = tuple[int, int](rng.choice([*opened]))


class _Wilson(_Algorithm):
    @staticmethod
    def wilson_erase(
        visited: NDArray, path: list[tuple], point: tuple[int, int]
    ) -> None:
        """Erase a loop during random walk"""
        while path[-1] != point:
            visited[path[-1][:]] = 0
            path.pop()

    def generate(self, maze: NDArray):
        self.gen_visited(maze)
        visited = self._visited
        yet = self.unvisited_set(visited)
        while len(yet) > 0:
            path = []
            current = rng.choice([*yet])
            visited[current[0], current[1]] = 2
            path.append(current)
            last_direction = ()
            while current in yet:
                direct = self.direction()
                while last_direction == direct:
                    direct = self.direction()
                try:
                    if direct[0] == "V":
                        if current[0] + direct[1] in (-1, maze.shape[0]):
                            raise IndexError
                        neighbour = (current[0] + direct[1], current[1])
                    else:
                        if current[1] + direct[1] in (
                            -1, maze.shape[1]
                        ):
                            raise IndexError
                        neighbour = (current[0], current[1] + direct[1])
                except IndexError:
                    continue
                if visited[neighbour[0], neighbour[1]] == -1:
                    continue
                elif visited[neighbour[0], neighbour[1]] == 1:
                    path.append(neighbour)
                    break
                elif neighbour in path:
                    self.wilson_erase(visited, path, neighbour)
                current = neighbour
                visited[current[0], current[1]] = 2
                if current not in path:
                    path.append(current)
            for tile in path:
                visited[tile[0], tile[1]] = 1
                yet.discard(tile)
            while len(path) > 1:
                self.connect(maze, path[-2], path[-1])
                current = path[-1]
                path.pop()
            path.clear()


class _AldousBroder(_Algorithm):
    def generate(self, maze: NDArray):
        self.gen_visited(maze)
        visited = self._visited
        current = self.maze_init(maze, visited)
        yet = self.unvisited_set(visited)
        while len(yet) > 0:
            direct = _Algorithm.direction()
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
                continue
            elif visited[neighbour[0], neighbour[1]] == 0:
                self.connect(maze, current, neighbour)
                yet.discard(neighbour)
            current = neighbour
            visited[current[0], current[1]] = 1


class _Imperfect(_Algorithm):
    @staticmethod
    def break_wall(maze: NDArray, tile: tuple[int, int], op: str) -> None:
        """Connect the chosen tiles"""
        i, j = tile[:]
        if op == "N":
            _Algorithm.connect(maze, tile, (i - 1, j))
        elif op == "E":
            _Algorithm.connect(maze, tile, (i, j + 1))
        elif op == "S":
            _Algorithm.connect(maze, tile, (i + 1, j))
        elif op == "W":
            _Algorithm.connect(maze, tile, (i, j - 1))

    @staticmethod
    def remove_walls(
        maze: NDArray, tile: tuple[int, int], prob: float = 1
    ) -> None:
        """Check for neighbouring removable walls"""
        if maze[tile[:]] == 15 or prob < 0 or prob > 1:
            return
        i, j = tile[:]
        walls = _Maze.get_walls(maze[tile[:]])
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
            _Imperfect.break_wall(maze, tile, rng.choice(r_walls))

    def generate(self, maze: NDArray):
        h, w = maze.shape
        """ Start connecting the four corners"""
        self.connect(maze, (0, 0), (0, 1))
        self.connect(maze, (0, 0), (1, 0))
        self.connect(maze, (0, w - 1), (0, w - 2))
        self.connect(maze, (0, w - 1), (1, w - 1))
        self.connect(maze, (h - 1, w - 1), (h - 1, w - 2))
        self.connect(maze, (h - 1, w - 1), (h - 2, w - 1))
        self.connect(maze, (h - 1, 0), (h - 1, 1))
        self.connect(maze, (h - 1, 0), (h - 2, 0))

        """Remove random walls in random tiles"""
        for _ in range(h * w // 3):
            tile = (rng.randrange(h), rng.randrange(w))
            _Imperfect.remove_walls(maze, tile, .5)
        dead_ends = (7, 11, 13, 14)
        s_wall = ((0, 1), (0, 2), (0, 4), (0, 8))
        adm_walls = [1, 2, 3, 4, 5, 6, 8, 9, 10, 12]

        """Remove dead ends; ignores 42"""
        for i in range(h):
            for j in range(w):
                if maze[i, j] in dead_ends:
                    _Imperfect.remove_walls(maze, (i, j))

        """Check for areas > 3x3; fill them in such case"""
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
                        walls = _Maze.get_walls(maze[i, j])
                        if walls[0] == 1:
                            maze[i - 1][j] += 4
                        if walls[1] == 1:
                            maze[i][j + 1] += 8
                        if walls[2] == 1:
                            maze[i + 1][j] += 1
                        if walls[3] == 1:
                            maze[i][j - 1] += 2


class _Maze:
    @staticmethod
    def get_walls(n: int) -> tuple[int, ...]:
        """Get the walls in a tile, return bit tuple"""
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

    @staticmethod
    def manhattan(curr: tuple[int, int], neigh: tuple[int, int]) -> int:
        """Manhattan heuristic, return distance"""
        return abs(curr[0] - neigh[0]) + abs(curr[1] - neigh[1])

    def __init__(
        self,
        height: int,
        width: int,
        perfect: bool,
        seed: int | None = None,
        algorithm: str = "Prim"
    ):
        self._height = height
        self._width = width
        self._perfect = perfect
        self._seed = seed
        self._algorithm = algorithm

    def generate(self):
        self._maze = 15 * ones([self._height, self._width])
        if self._solution:
            self.solution = ""
        if self._algorithm.lower() in (
            "dfs", "recursive backtracker", "depth first search"
        ):
            algo = _DFS()
        elif self._algorithm.lower() in (
            "ab", "aldous broder", "aldous-broder"
        ):
            algo = _AldousBroder()
        elif self._algorithm.lower() == "wilson":
            algo = _Wilson()
        else:
            algo = _Prim()
        algo.generate(self._maze, self._seed)
        if self._perfect is False:
            imp = _Imperfect()
            imp.generate(self._maze, self._seed)

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def perfect(self):
        return self._perfect

    @property
    def seed(self):
        return self._seed

    @property
    def algorithm(self):
        return self._algorithm


class _Path:
    def __init__(self, entry: tuple[int, int], exit: tuple[int, int]):
        self.entry = entry
        self.exit = exit
        self._path = ""

    class _Node:
        def __init__(self, val: tuple[int, int]):
            self.val = val
            self._g = inf
            self._h = inf
            self._f = inf
            self.next: None | _Path._Node = None

        def add_front(self, new):
            new.next = self
            self = new

        def size(self) -> int:
            n = 1
            current = self
            while current.next is not None:
                current = current.next
                if current is self:
                    break
                n += 1
            return n

        def get_g(self) -> int:
            return int(self._g)

        def get_h(self) -> int:
            return int(self._h)

        def get_f(self) -> int:
            return int(self._f)

        def _set_f(self, f: int) -> None:
            self._f = f

        def set_g(self, g: int) -> None:
            self._g = g
            self._set_f(self.get_g() + self.get_h())

        def set_h(self, h: int) -> None:
            self._h = h
            self._set_f(self.get_g() + self.get_h())

    @staticmethod
    def neighbours(
        maze: NDArray, current: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """Return reachable neighbours list from a maze tile"""
        n = maze[current[:]]
        neighs = []
        walls = _Maze.get_walls(n)
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
    def choose_current(
        f: NDArray, points: list[_Node], exit: tuple[int, int]
    ) -> _Node:
        """Return most promising point to evaluate"""
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
            h = _Maze.manhattan(k.val, exit)
            if h < min_h:
                min_h = h
                current = k
        return current

    @staticmethod
    def check_node(set: set[_Node], point: tuple[int, int]) -> bool:
        """Check point in a set"""
        for i in set:
            if i.val == point:
                return True
        return False

    def solve(
        self, maze: NDArray, entr: tuple[int, int], exit: tuple[int, int]
    ) -> None:
        """A* pathfinding algorithm with Manhattan heuristic"""

        opened, closed = set(), set()
        f_cost = inf * ones(maze.shape[:], int)
        opened.add(self._Node(entr))
        f_cost[entr[:]] = _Maze.manhattan(entr, exit)
        while len(opened) > 0:
            """Choose current node, move from open list to closed list"""
            current = self.choose_current(f_cost, list(opened), exit)
            opened.remove(current)
            closed.add(current)
            """If node is the exit, path has been found"""
            if current.val == exit:
                break
            for i in self.neighbours(maze, current.val):
                """If node is already closed, continue"""
                if self.check_node(closed, i) is True:
                    continue
                node = self._Node(i)
                node.next = current
                node.set_g(node.size() - 1)
                node.set_h(_Maze.manhattan(i, exit))
                """Update F cost if is lower"""
                if node.get_f() < f_cost[i[:]]:
                    f_cost[i[:]] = node.get_f()
                    if self.check_node(opened, i) is True:
                        if _Maze.manhattan(i, entr) > node.get_g():
                            continue
                    opened.add(node)

        """Return the maze solution via backtracking"""
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
        self._path = sol

    @property
    def path(self):
        return self._path


class MazeGenerator:

    def __init__(
        self,
        height: int,
        width: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        perfect: bool,
        seed: int | None = None,
        algorithm: str = "Prim"
    ):
        self._maze = _Maze(height, width, perfect, seed, algorithm)
        self._entry = entry
        self._exit = exit

    def generate(self):
        self._maze.generate()

    def solve(self):
        path = self.Path(self._entry, self.exit)
        self._solution = path.solve(self._maze)

    def draw(self):
        """Draw the maze"""
        pass

    @property
    def entry(self):
        return self._entry

    @property
    def exit(self):
        return self._exit
