from numpy import ones
from abc import ABC


class MazeGenerator:
    class Algorithm(ABC):
        def generate(self, maze: Maze):
            pass
            
        def maze_init(maze: NDArray, visited: NDArray) -> tuple[int]:
            h, w = maze.shape[:]
            v = -1
            while v == -1:
                current = (
                    rng.randrange(0, h - 1), rng.randrange(0, w - 1)
                )
                v = visited[current[:]]
            visited[current[:]] = 1
            return current

        def connect(
            maze: NDArray, curr: tuple[int], neigh: tuple[int]
        ) -> None:
            """Connect two maze tiles"""
            if manhattan(curr, neigh) != 1:
                return
            if curr[0] == neigh[0] + 1 and get_walls(maze[curr[:]])[0] == 1:
                maze[curr[0]][curr[1]] -= 1
                maze[neigh[0]][neigh[1]] -= 4
            if curr[0] == neigh[0] - 1 and get_walls(maze[curr[:]])[2] == 1:
                maze[curr[0]][curr[1]] -= 4
                maze[neigh[0]][neigh[1]] -= 1
            if curr[1] == neigh[1] - 1 and get_walls(maze[curr[:]])[1] == 1:
                maze[curr[0]][curr[1]] -= 2
                maze[neigh[0]][neigh[1]] -= 8
            if curr[1] == neigh[1] + 1 and get_walls(maze[curr[:]])[3] == 1:
                maze[curr[0]][curr[1]] -= 8
                maze[neigh[0]][neigh[1]] -= 2

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
            
    class DFS(Algorithm):
        def generate(self, maze: Maze):
            current = maze_init(maze, visited)
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
                    connect(maze, current, new)
                    visited[new[:]] = 1
                    lst.append(new)
                try:
                    current = lst[-1]
                except IndexError:
                    pass
            
    class Prim(Algorithm):
        def unvisited_set(visited: NDArray) -> set:
            """Make the unvisited tiles set"""
            yet = set()
            for i in range(visited.shape[0]):
                for j in range(visited.shape[1]):
                    if visited[i, j] == 0:
                        yet.add((i, j))
            return yet

        def generate(self, maze: Maze):
            current = maze_init(maze, visited)
            yet = unvisited_set(visited)
            opened = set()
            opened.add(tuple(current))
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
                    connect(maze, current, new)
                    visited[new[:]] = 1
                    opened.add(new)
                if len(opened) > 0:
                    current = rng.choice([*opened])
            
    class Wilson(Algorithm):
        def wilson_erase(
            visited: NDArray, path: list[tuple], point: tuple[int]
        ) -> None:
            """Erase a loop during random walk"""
            while path[-1] != point:
                visited[path[-1][:]] = 0
                path.pop()

        def generate(self, maze: Maze):
            yet = unvisited_set(visited)
            while len(yet) > 0:
                path = []
                current = rng.choice([*yet])
                visited[current[0], current[1]] = 2
                path.append(current)
                last_direction = ()
                while current in yet:
                    direct = direction()
                    while last_direction == direct:
                        direct = direction()
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
                        wilson_erase(visited, path, neighbour)
                    current = neighbour
                    visited[current[0], current[1]] = 2
                    if current not in path:
                        path.append(current)
                for tile in path:
                    visited[tile[0], tile[1]] = 1
                    yet.discard(tile)
                while len(path) > 1:
                    connect(maze, path[-2], path[-1])
                    current = path[-1]
                    path.pop()
                path.clear()
            
    class AldousBroder(Algorithm):
        def generate(self, maze: Maze):
            current = maze_init(maze, visited)
            yet = unvisited_set(visited)
            while len(yet) > 0:
                direct = direction()
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
                    connect(maze, tuple(current), tuple(neighbour))
                    yet.discard(neighbour)
                current = neighbour
                visited[current[0], current[1]] = 1

        class Imperfect(Algorithm):
            def generate(self, maze: Maze):
                h, w = maze.shape
                """ Start connecting the four corners"""
                connect(maze, (0, 0), (0, 1))
                connect(maze, (0, 0), (1, 0))
                connect(maze, (0, w - 1), (0, w - 2))
                connect(maze, (0, w - 1), (1, w - 1))
                connect(maze, (h - 1, w - 1), (h - 1, w - 2))
                connect(maze, (h - 1, w - 1), (h - 2, w - 1))
                connect(maze, (h - 1, 0), (h - 1, 1))
                connect(maze, (h - 1, 0), (h - 2, 0))
            
                """Remove random walls in random tiles"""
                for _  in range(h * w // 3):
                    tile = (rng.randrange(h), rng.randrange(w))
                    remove_walls(maze, tile, .5)
                dead_ends = (7, 11, 13, 14)
                s_wall = ((0, 1), (0, 2), (0, 4), (0, 8))
                adm_walls = [1, 2, 3, 4, 5, 6, 8, 9, 10, 12]
            
                """Remove dead ends; ignores 42"""
                for i in range(h):
                    for j in range(w):
                        if maze[i, j] in dead_ends:
                            remove_walls(maze, (i, j))
            
                """Check for areas > 3x3; fill them in such case"""
                for i in range(h):
                    for j in range(w):
                        if maze[i, j] == 0:
                            adj_tiles = [
                                (i - 1, j), (i, j + 1), (i + 1, j), (i, j - 1)
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

    class Maze:
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
            self._maze = 15 * ones([height, width])
            if self._solution:
                self.solution = ""
            if algorithm.lower() in (
                "dfs", "recursive backtracker", "depth first search"
            ):
                dfs(self._maze, seed)
            elif algorithm.lower() in (
                "ab", "aldous broder", "aldous-broder"
            ):
                aldous_broder(self._maze, seed)
            elif algorithm.lower() == "wilson":
                wilson(self._maze, seed)
            else:
                prim(self._maze, seed)
            if perfect is False:
                imperfect(self._maze)

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

    class Path:
        def __init__(self, entry: tuple[int, int], exit: tuple[int, int]):
            self.entry = entry
            self.exit = exit
            self._path = ""

        class Node:
            def __init__(self, val: tuple[int, int]):
                self.val = val
                self._g = inf
                self._h = inf
                self._f = inf
                self.next = None

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
                return self._g
        
            def get_h(self) -> int:
                return self._h
        
            def get_f(self) -> int:
                return self._f
        
            def _set_f(self, f: int) -> None:
                self._f = f
        
            def set_g(self, g: int) -> None:
                self._g = g
                self._set_f(self.get_g() + self.get_h())
        
            def set_h(self, h: int) -> None:
                self._h = h
                self._set_f(self.get_g() + self.get_h())

        def neighbours(maze: NDArray, current: tuple[int]) -> list[tuple]:
            """Return reachable neighbours list from a maze tile"""
            n = maze[current[:]]
            neighs = []
            walls: tuple[int] = get_walls(n)
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
            f: NDArray, points: list[Node], exit: tuple[int]
        ) -> Node:
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

        def check_node(set: set[Node], point = tuple[int]) -> bool:
            """Check point in a set"""
            for i in set:
                if i.val == point:
                    return True
            return False

        def solve(maze: NDArray, entr: tuple[int], exit: tuple[int]) -> str:
            """A* pathfinding algorithm with Manhattan heuristic"""

            opened, closed = set(), set()
            f_cost = inf * ones(maze.shape[:], int)
            opened.add(Node(entr))
            f_cost[entr[:]] = manhattan(entr, exit)
            while len(opened) > 0:
                """Choose current node, move from open list to closed list"""
                current = choose_current(f_cost, list(opened), exit)
                opened.remove(current)
                closed.add(current)
                """If node is the exit, path has been found"""
                if current.val == exit:
                    break
                for i in neighbours(maze, current.val):
                    """If node is already closed, continue"""
                    if check_node(closed, i) is True:
                        continue
                    node = Node(i)
                    node.next = current
                    node.set_g(node.size() - 1)
                    node.set_h(manhattan(i, exit))
                    """Update F cost if is lower"""
                    if node.get_f() < f_cost[i[:]]:
                        f_cost[i[:]] = node.get_f()
                        if check_node(opened, i) is True:
                            if manhattan(i, entr) > node.get_g():
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
            return sol

        @property
        def path(self):
            return self._path

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
        self._maze = self.Maze(height, width, perfect, seed, algorithm)
        self._entry = entry
        self._exit = exit

    def generate(self):
        self._maze.generate()

    def solve(self):
        path = Path(self._entry, self.exit)
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
