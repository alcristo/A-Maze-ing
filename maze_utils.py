from numpy.typing import NDArray


class MazeError(Exception):
    def __init__(self, msg: str = ""):
        self.msg = msg


def manhattan(curr: tuple[int, int], neigh: tuple[int, int]) -> int:
    """Manhattan heuristic, return distance"""
    return abs(curr[0] - neigh[0]) + abs(curr[1] - neigh[1])


def check_errors(conf: dict):
    """Check for errors in the configuration"""
    start = conf["ENTRY"].split(",")
    end = conf["EXIT"].split(",")
    try:
        entr = (int(start[1]), int(start[0]))
        exit = (int(end[1]), int(end[0]))
        size = (int(conf["HEIGHT"]), int(conf["WIDTH"]))
    except ValueError:
        raise MazeError(
            "[ERROR] Configurtion is in wrong format. "
            "Please, use integers for HEIGHT, WIDTH, ENTRY & EXIT"
        )
    except IndexError:
        raise MazeError(
            "[ERROR] Entry or exit in wrong format. "
            "Usage ex.: EXIT=[int],[int]"
        )

    """Check that entry and exit are actually different"""
    if entr == exit:
        raise MazeError("Maze entrance and exit must be different")

    """Check positive height and width"""
    if size[0] <= 0 or size[1] <= 0:
        raise MazeError("Maze dimensions must be positive")

    in_bounds = [
        entr[0] >= 0,
        entr[1] >= 0,
        entr[0] < size[0],
        entr[1] < size[1],
        exit[0] >= 0,
        exit[1] >= 0,
        exit[0] < size[0],
        exit[1] < size[1]
    ]
    if size[0] > 5 and size[1] > 7:
        hs = (size[0] - 1) // 2 - 2
        ws = (size[1] - 1) // 2 - 3
        pos_42 = (
            (hs, ws), (hs + 1, ws), (hs + 2, ws), (hs + 2, ws + 1),
            (hs + 2, ws + 2), (hs + 3, ws + 2), (hs + 4, ws + 2),
            (hs, ws + 4), (hs, ws + 5), (hs, ws + 6), (hs + 1, ws + 6),
            (hs + 2, ws + 6), (hs + 2, ws + 5), (hs + 2, ws + 4),
            (hs + 3, ws + 4), (hs + 4, ws + 4), (hs + 4, ws + 5),
            (hs + 4, ws + 6)
        )
    if False in in_bounds:
        raise MazeError(
            "Entrance or exit of the maze seem to be out of bounds"
        )

    if size[0] > 5 and size[1] > 7:
        if True in [entr in pos_42, exit in pos_42]:
            raise MazeError(
                "Entrance or exit of the maze seem to be inside the 42"
            )


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


def check_tile(maze: NDArray, coords: tuple[int, int]):
    """Check coherence between tile walls"""
    i, j = coords
    tile = int(maze[i, j])
    msg = f"Maze tile {coords} has incoherent walls"
    walls = get_walls(tile)
    if i == 0:
        if walls[0] == 0:
            raise MazeError(f"{msg} with north border")
    else:
        if walls[0] != get_walls(maze[i - 1][j])[2]:
            raise MazeError(f"{msg} with tile {(i - 1, j)}")
    if i == maze.shape[0] - 1:
        if walls[2] == 0:
            raise MazeError(f"{msg} with south border")
    else:
        if walls[2] != get_walls(maze[i + 1][j])[0]:
            raise MazeError(f"{msg} with tile {(i + 1, j)}")
    if j == 0:
        if walls[3] == 0:
            raise MazeError(f"{msg} with west border")
    else:
        if walls[3] != get_walls(maze[i][j - 1])[1]:
            raise MazeError(f"{msg} with tile {(i, j - 1)}")
    if j == maze.shape[1] - 1:
        if walls[1] == 0:
            raise MazeError(f"{msg} with east border")
    else:
        if walls[1] != get_walls(maze[i][j + 1])[3]:
            raise MazeError(f"{msg} with tile {(i, j + 1)}")
