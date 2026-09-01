from __future__ import annotations
from numpy import zeros, ones, inf
from numpy.typing import NDArray
from typing import Any
from abc import ABC, abstractmethod
import sys
import random as rng


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


def manhattan(curr: tuple[int, int], neigh: tuple[int, int]) -> int:
    """Manhattan heuristic, return distance"""
    return abs(curr[0] - neigh[0]) + abs(curr[1] - neigh[1])


class _Algorithm(ABC):

    @abstractmethod
    def generate(self, maze: NDArray[Any], seed: int | None = None) -> None:
        pass

    @staticmethod
    def unvisited_set(visited: NDArray[Any]) -> set[tuple[int, int]]:
        """Make the unvisited tiles set"""
        yet = set()
        for i in range(visited.shape[0]):
            for j in range(visited.shape[1]):
                if visited[i, j] == 0:
                    yet.add((i, j))
        return yet

    @staticmethod
    def maze_init(
        maze: NDArray[Any], visited: NDArray[Any], seed: None | int
    ) -> tuple[int, int]:
        h, w = maze.shape[:]
        v = -1
        rng.seed(seed)
        while v == -1:
            current = (rng.randrange(0, h - 1), rng.randrange(0, w - 1))
            v = visited[current[:]]
        visited[current[:]] = 1
        return current

    @staticmethod
    def connect(
        maze: NDArray[Any], curr: tuple[int, int], neigh: tuple[int, int]
    ) -> None:
        """Connect two maze tiles"""
        if manhattan(curr, neigh) != 1:
            return
        if curr[0] == neigh[0] + 1 and get_walls(
            maze[curr[:]]
        )[0] == 1:
            maze[curr[0]][curr[1]] -= 1
            maze[neigh[0]][neigh[1]] -= 4
        if curr[0] == neigh[0] - 1 and get_walls(
            maze[curr[:]]
        )[2] == 1:
            maze[curr[0]][curr[1]] -= 4
            maze[neigh[0]][neigh[1]] -= 1
        if curr[1] == neigh[1] - 1 and get_walls(
            maze[curr[:]]
        )[1] == 1:
            maze[curr[0]][curr[1]] -= 2
            maze[neigh[0]][neigh[1]] -= 8
        if curr[1] == neigh[1] + 1 and get_walls(
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

    def gen_visited(self, maze: NDArray[Any]) -> None:
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
    def generate(self, maze: NDArray[Any], seed: int | None = None) -> None:
        self.gen_visited(maze)
        visited = self._visited
        current = self.maze_init(maze, visited, seed)
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

    def generate(self, maze: NDArray[Any], seed: int | None = None) -> None:
        self.gen_visited(maze)
        visited = self._visited
        rng.seed(seed)
        current = self.maze_init(maze, visited, seed)
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
        visited: NDArray[Any],
        path: list[tuple[int, int]],
        point: tuple[int, int]
    ) -> None:
        """Erase a loop during random walk"""
        while path[-1] != point:
            visited[path[-1][:]] = 0
            path.pop()

    def generate(self, maze: NDArray[Any], seed: int | None = None) -> None:
        self.gen_visited(maze)
        visited = self._visited
        current = self.maze_init(maze, visited, seed)
        yet = self.unvisited_set(visited)
        while len(yet) > 0:
            path = []
            current = rng.choice([*yet])
            visited[current[0], current[1]] = 2
            path.append(current)
            last_direction = ("x", 0)
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
                        if current[1] + direct[1] in (-1, maze.shape[1]):
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
    def generate(self, maze: NDArray[Any], seed: int | None = None) -> None:
        self.gen_visited(maze)
        visited = self._visited
        rng.seed(seed)
        current = self.maze_init(maze, visited, seed)
        yet = self.unvisited_set(visited)
        while len(yet) > 0:
            direct = self.direction()
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
    def break_wall(
        self, maze: NDArray[Any], tile: tuple[int, int], op: str
    ) -> None:
        """Connect the chosen tiles"""
        i, j = tile[:]
        if op == "N":
            self.connect(maze, tile, (i - 1, j))
        elif op == "E":
            self.connect(maze, tile, (i, j + 1))
        elif op == "S":
            self.connect(maze, tile, (i + 1, j))
        elif op == "W":
            self.connect(maze, tile, (i, j - 1))

    def remove_walls(
        self, maze: NDArray[Any], tile: tuple[int, int], prob: float = 1
    ) -> None:
        """Check for neighbouring removable walls"""
        if maze[tile[:]] == 15 or prob < 0 or prob > 1:
            return
        i, j = tile[:]
        walls = get_walls(maze[tile[:]])
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
            self.break_wall(maze, tile, rng.choice(r_walls))

    def generate(self, maze: NDArray[Any], seed: int | None = None) -> None:
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
            self.remove_walls(maze, tile, .5)
        dead_ends = (7, 11, 13, 14)
        s_wall = ((0, 1), (0, 2), (0, 4), (0, 8))
        adm_walls = [1, 2, 3, 4, 5, 6, 8, 9, 10, 12]

        """Remove dead ends; ignores 42"""
        for i in range(h):
            for j in range(w):
                if maze[i, j] in dead_ends:
                    self.remove_walls(maze, (i, j))

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
                        walls = get_walls(maze[i, j])
                        if walls[0] == 1:
                            maze[i - 1][j] += 4
                        if walls[1] == 1:
                            maze[i][j + 1] += 8
                        if walls[2] == 1:
                            maze[i + 1][j] += 1
                        if walls[3] == 1:
                            maze[i][j - 1] += 2


class _Maze:

    def __init__(
        self,
        height: int,
        width: int,
        perfect: bool,
        seed: int | None = None,
        algorithm: str = "Prim"
    ) -> None:
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

    def generate(self) -> None:
        self._maze = 15 * ones([self._height, self._width], int)
        self._algo.generate(self._maze, self._seed)
        if self._perfect is False:
            imp = _Imperfect()
            imp.generate(self._maze, self._seed)

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
    def seed(self) -> int | None:
        return self._seed

    @property
    def algorithm(self) -> _Algorithm:
        return self._algo

    @property
    def maze(self) -> NDArray[Any]:
        return self._maze


class _Node:
    def __init__(self, value: Any) -> None:
        self.val = value
        self._g = inf
        self._h = inf
        self._f = inf
        self.next: Any = None

    def size(self) -> int:
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


class _Path:

    """class _Node:
        def __init__(self, value: Any) -> None:
            self.val = value
            self._g = inf
            self._h = inf
            self._f = inf
            self.next = None

        def size(self) -> int:
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
            self._set_f(self.get_g() + self.get_h())"""

    def __init__(
        self,
        maze: NDArray[Any],
        entry: tuple[int, int],
        exit: tuple[int, int]
    ) -> None:
        self._entry = entry
        self._exit = exit
        self._maze = maze
        self._path = ""
        self._checked = 0

    def __str__(self) -> str:
        return self._path

    @staticmethod
    def neighbours(
        maze: NDArray[Any], current: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """Return reachable neighbours list from a maze tile"""
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

    @staticmethod
    def choose_current(
        f: NDArray[Any], points: list[_Node], exit: tuple[int, int]
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
            h = manhattan(k.val, exit)
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

    @staticmethod
    def rm_node(
        set: set[_Node], point: tuple[int, int], new: _Node
    ) -> None:
        alt_path = []
        for n in set:
            if n.val == new.val:
                alt_path.append(n)

        for n in alt_path:
            if new.get_g() < n.get_g():
                set.remove(n)
        if len(alt_path) == 0:
            set.add(new)

    @staticmethod
    def add_front(old: _Node, newnode: _Node) -> None:
        if newnode is None:
            return
        newnode.next = old

    def solve(self) -> str:
        """A* pathfinding algorithm with Manhattan heuristic"""

        opened, closed = set(), set()
        g_cost = inf * ones(self._maze.shape[:], int)
        f_cost = inf * ones(self._maze.shape[:], int)
        opened.add(_Node(self._entry))
        f_cost[self._entry[:]] = manhattan(self._entry, self._exit)
        g_cost[self._entry[:]] = 0
        self._checked = 0
        while len(opened) > 0:
            self._checked += 1
            """Choose current node, move from open list to closed list"""
            current = self.choose_current(f_cost, list(opened), self._exit)
            opened.remove(current)
            closed.add(current)
            """If node is the exit, path has been found"""
            if current.val == self._exit:
                break
            for i in self.neighbours(self._maze, current.val):
                """If node is already closed, continue"""
                if self.check_node(closed, i) is True:
                    continue
                node = _Node(i)
                self.add_front(current, node)
                node.set_g(node.size() - 1)
                if node.get_g() < g_cost[i[:]]:
                    g_cost[i[:]] = node.get_g()
                    self.rm_node(opened, i, node)
                else:
                    continue
                node.set_h(manhattan(i, self._exit))
                """Update F cost if is lower"""
                if node.get_f() < f_cost[i[:]] or self.check_node(
                    opened, i
                ) is False:
                    f_cost[i[:]] = node.get_f()
                    if self.check_node(opened, i) is False:
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
        return sol

    @property
    def checked(self) -> int:
        return self._checked

    @property
    def path(self) -> str:
        return self._path


def valid_entry_exit(
    size: tuple[int, int], entry: tuple[int, int], exit: tuple[int, int]
) -> None:
    if entry == exit:
        print("[ERROR] Entry and exit must not be equal", file=sys.stderr)
        raise ValueError
    en = (
        entry[0] < 0 or entry[0] >= size[0],
        entry[1] < 0 or entry[1] >= size[1]
    )
    if True in en:
        print("[ERROR] Entry is out of bounds", file=sys.stderr)
        raise ValueError
    ex = (
        exit[0] < 0 or exit[0] >= size[0],
        exit[1] < 0 or exit[1] >= size[1]
    )
    if True in ex:
        print("[ERROR] Exit is out of bounds", file=sys.stderr)
        raise ValueError
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
        if entry in pos_42:
            print("[ERROR] Entry is inside '42'", file=sys.stderr)
            raise ValueError
        if exit in pos_42:
            print("[ERROR] Exit is inside '42'", file=sys.stderr)
            raise ValueError


class MazeGenerator:

    def __init__(self, config_file: str) -> None:
        with open(config_file) as f:
            txt = f.read()
            opts = txt.split("\n")
            tup = [tuple(i.split("=")) for i in opts if "=" in i]
            conf = {i[0].upper(): i[1] for i in tup if i[0][0] != "#"}
        try:
            height = int(conf["HEIGHT"])
            width = int(conf["WIDTH"])
            assert height > 0
            assert width > 0
            en = conf["ENTRY"].split(",")
            entry = (int(en[1]), int(en[0]))
            ex = conf["EXIT"].split(",")
            exit = (int(ex[1]), int(ex[0]))
        except AssertionError:
            print("[ERROR] Maze dimensions must be positive", file=sys.stderr)
            return
        except KeyError as e:
            print(f"[ERROR] Invalid configuration: {e}")
            return
        except ValueError as e:
            print(f"[ERROR] Configuration in wrong format: {e}")
            return
        except IndexError:
            print("[ERROR] Entry/Exit in wrong format. Usage ex.: EXIT=0,0")
            return
        try:
            valid_entry_exit((height, width), entry, exit)
        except ValueError:
            return
        perfect = conf.get("PERFECT", "True").lower() != "false"
        try:
            seed = int(conf["SEED"])
        except KeyError:
            seed = None
        algorithm = conf.get("ALGORITHM", "Prim")
        self._maze = _Maze(height, width, perfect, seed, algorithm)
        self._entry = entry
        self._exit = exit
        self._output_file = conf.get("OUTPUT_FILE", "output_maze.txt")

    def _generate(self) -> None:
        try:
            self._maze.generate()
        except AttributeError:
            return

    def _solve(self) -> None:
        try:
            path = _Path(self._maze._maze, self._entry, self._exit)
            self._solution = path.solve()
        except AttributeError:
            print("[ERROR] No maze to solve", file=sys.stderr)

    def _draw(self) -> None:
        pathtiles = []
        curr = self._entry
        for dir in self._solution:
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
        black = "\x1b[40m"
        red = "\x1b[41m"
        green = "\x1b[42m"
        # yellow = "\x1b[43m"
        blue = "\x1b[44m"
        magenta = "\x1b[45m"
        # cyan = "\x1b[46m"
        white = "\x1b[47m"

        h, w = self._maze._maze.shape
        for _ in range(2 * w + 1):
            print(f"{black}  {reset}", end="")
        print()
        i = 0
        for i in range(h):
            print(f"{black}  {reset}", end="")
            for j in range(w):
                n = self._maze._maze[i, j]
                if n == 15:
                    print(f"{red}  {reset}", end="")
                elif (i, j) == self._entry:
                    print(f"{magenta}  {reset}", end="")
                elif (i, j) == self._exit:
                    print(f"{green}  {reset}", end="")
                elif (i, j) in pathtiles:
                    print(f"{blue}  {reset}", end="")
                else:
                    print(f"{white}  {reset}", end="")
                if (i, j) in pathtiles and (
                    i, j + 1
                ) in pathtiles and get_walls(n)[1] == 0:
                    print(f"{blue}  {reset}", end="")
                elif get_walls(n)[1] == 0:
                    print(f"{white}  {reset}", end="")
                else:
                    print(f"{black}  {reset}", end="")
            print()
            print(f"{black}  {reset}", end="")
            for j in range(w):
                n = self._maze._maze[i, j]
                if (i, j) in pathtiles and (
                    i + 1, j
                ) in pathtiles and get_walls(n)[2] == 0:
                    print(f"{blue}  {reset}", end="")
                elif get_walls(n)[2] == 0:
                    print(f"{white}  {reset}", end="")
                else:
                    print(f"{black}  {reset}", end="")
                print(f"{black}  {reset}", end="")
            print()

    def _output(self) -> None:
        base = "0123456789abcdef"
        try:
            self._maze
        except AttributeError:
            print("[ERROR] No maze to print", file=sys.stderr)
            return
        with open(self._output_file, 'w') as out:
            for i in range(self._maze.height):
                for j in range(self._maze.width):
                    out.write(base[self._maze._maze[i, j]])
                out.write("\n")
            out.write("\n")
            out.write(f"{self._entry[1]},{self._entry[0]}\n")
            out.write(f"{self._exit[1]},{self._exit[0]}\n")
            print(self._solution)
            out.write(self._solution)

    def regen(self) -> None:
        try:
            self._generate()
            self._solve()
            self._draw()
        except AttributeError:
            return
        clear = "\x1bc"
        while True:
            print("=== A-Maze-ing ===")
            print("1. Generate a new maze")
            print("2. Show/hide solution")
            print("3. Change colors")
            print("q. Quit")
            opt = input()
            if opt == "1":
                print(f"{clear}")
                self.regen()
                continue
            elif opt == "2":
                print(self._solution)
                continue
            elif opt == "3":
                R = int(input("R:"))
                if R < 0 or R > 255:
                    print("Invalid color")
                    continue
                G = int(input("G:"))
                if G < 0 or G > 255:
                    print("Invalid color")
                    continue
                B = int(input("B:"))
                if B < 0 or B > 255:
                    print("Invalid color")
                    continue
                print("Color: {hex(R)}{hex(G)}{hex(B)}")
                continue
            elif opt == "q":
                sys.exit()
            else:
                continue

    @property
    def maze(self) -> _Maze:
        return self._maze

    @property
    def solution(self) -> str:
        return self._solution
