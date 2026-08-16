from sys import argv, exit
from numpy import zeros, ones, mean, array
from numpy.typing import NDArray
from maze_utils import *
from maze_algos import wilson, aldous_broder
from pathfinding import a_star
import random as rng


def main() -> None:
    """Open the configuration file and set everything"""
    with open(argv[1]) as f:
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
    wilson(maze, visited)
    """Solution"""
    start = conf["ENTRY"].split(",")
    end = conf["EXIT"].split(",")
    entr = (int(start[0]), int(start[1]))
    exit = (int(end[0]), int(end[1]))
    sol = a_star(maze, entr, exit)

    """Save the file"""
    base = "0123456789abcdef"
    txt = ""
    with open(conf['OUTPUT_FILE'], 'w') as out:
        for i in range(size[0]):
            for j in range(size[1]):
                out.write(base[maze[i][j]])
            out.write("\n")
        out.write("\n")
        out.write(f"{entr}          # entry (x,y)\n")
        out.write(f"{exit}          # exit (x,y)\n")
        out.write(sol)


if __name__ == "__main__":
    if len(argv) != 2:
        print("Only one configuration file is allowed")
        exit()
    try:
        main()
    except KeyboardInterrupt:
        print("Program terminated by user")
