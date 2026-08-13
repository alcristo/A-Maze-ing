from numpy import zeros, ones, mean, array
from numpy.typing import NDArray
import random as rng


class MazeError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


"""Check for errors in the configuration"""
def check_errors(conf: dict):
    start = conf["ENTRY"].split(",")
    end = conf["EXIT"].split(",")
    entr = (int(start[0]), int(start[1]))
    exit = (int(end[0]), int(end[1]))

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
    if False in in_bounds:
        raise MazeError(
            "Entrance or exit of the maze seem to be out of bounds"
        )
    
    if visited.shape[0] > 6 or visited.shape[1] > 8:
        in_42 = []
        in_42.extend([True for i in pos_42 if i[0] == entr[0] and i[1] == entr[1]])
        in_42.extend([True for i in pos_42 if i[0] == exit[0] and i[1] == exit[1]])
        if True in in_42:
            raise MazeError("Entrance or exit of the maze seem to be inside the 42")


"""Get the walls in a tile, return bit tuple"""
def get_walls(n: int) -> tuple[int]:
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


"""Check coherence between tile walls"""
def check_tile(maze: NDArray, coords: tuple[int]):
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


def main() -> None:
    """Open the configuration file and set everything"""
    with open("config.txt") as f:
        txt = f.read()
        opts = txt.split("\n")
        tup = [tuple(i.split("=")) for i in opts]
        conf = {i[0]: i[1] for i in tup}
    try:
        check_errors(conf)
    except MazeError as e:
        print(e.msg)
        return

    """Create the maze and visited tiles arrays"""
    size = (int(conf["HEIGHT"]), int(conf["WIDTH"]))
    maze = ones(size, int) * 15
    visited = zeros(size, int)
    perfect = bool(conf["PERFECT"])
    if visited.shape[0] < 7 and visited.shape[1] < 9:
        is_42 = 0
        print("The '42' cannot be printed in a maze this size.")
    else:
        is_42 = 1
        hs, ws = visited.shape[0] // 2 - 2, visited.shape[1] // 2 - 3
        pos_42 = (
            (hs, ws), (hs + 1, ws), (hs + 2, ws), (hs + 2, ws + 1),
            (hs + 2, ws + 2), (hs + 3, ws + 2), (hs + 4, ws + 2),
            (hs, ws + 4), (hs, ws + 5), (hs, ws + 6), (hs + 1, ws + 6),
            (hs + 2, ws + 6), (hs + 2, ws + 5), (hs + 2, ws + 4),
            (hs + 3, ws + 4), (hs + 4, ws + 4), (hs + 4, ws + 5),
            (hs + 4, ws + 6)
        )
        for i in pos_42:
            visited[i[0]][i[1]] = -1

    """Place first tile in the maze"""
    current = [rng.randrange(0, size[0] - 1), rng.randrange(0, size[1] - 1)]
    visited[current[0]][current[1]] = 1
    """Algorithm"""
    maze_algo(maze, visited)

    """Print the hexadecimal maze"""
    base = "0123456789abcdef"
    for i in range(maze.shape[0]):
        for j in range(maze.shape[1]):
            try:
                check_tile(maze, (i, j))
                print(base[maze[i][j]], end="")
            except MazeError as e:
                print(e.msg)
        print()txt = ""
    with open(conf['OUTPUT_FILE'], 'w') as out:
        print(maze)
        for i in range(size[0]):
            for j in range(size[1]):
                out.write(base[maze[i][j]])
            out.write("\n")

        out.write("\n")
        out.write(f"{entr}          # entry (x,y)\n")
        out.write(f"{exit}          # exit (x,y)\n")


if __name__ == "__main__":
    main()
