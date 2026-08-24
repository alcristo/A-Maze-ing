from numpy import ones


class MazeGenerator:
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
            if algorithm.lower() in ("dfs", "recursive backtracker", "depth first search"):
                dfs(self._maze, seed)
            elif algorithm.lower() in ("ab", "aldous broder", "aldous-broder"):
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

        class Node:
            def __init__(self, val: tuple[int, int], next: cls | None = None):

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

    def solve(self):
        self._solution = a_star(self._maze)

    def draw(self):
        """Draw the maze"""
        pass

    @property
    def entry(self):
        return self._entry

    @property
    def exit(self):
        return self._exit
