from sys import argv, stderr, exit
from numpy import zeros, ones, mean, array
from numpy.typing import NDArray
from maze_utils import MazeError, check_errors
from maze_algos import dfs, prim, wilson, aldous_broder, imperfect
from pathfinding import a_star
import random as rng
from signal import SIGINT, signal, raise_signal


def select_algo(conf: dict) -> str:
    try:
        if conf["ALGORITHM"].lower() in (
            "aldous broder", "aldousbroder", "aldous_broder", "aldous-broder"
        ):
            return "AldousBroder"
        elif conf["ALGORITHM"].lower() in (
            "dfs", "depthfirstsearch", "depth first search", "depth_first_search",
            "recursivebacktracker", "recursive backtracker",
            "recursive_backtracker"
        ):
            return "DFS"
        elif conf["ALGORITHM"].lower() == "prim":
            return "Prim"
        elif conf["ALGORITHM"].lower() == "wilson":
            return "Wilson"
        else:
            return "Error"
    except KeyError:
        return "Prim"


def main() -> None:
    """Open the configuration file and set everything"""
    with open(argv[1]) as f:
        txt = f.read()
        opts = txt.split("\n")
        tup = [tuple(i.split("=")) for i in opts]
        conf = {i[0].upper(): i[1] for i in tup if i[0][0] != "#"}
    try:
        check_errors(conf)
    except MazeError as e:
        print(e.msg, file=stderr)
        return

    """Create the maze and visited tiles arrays"""
    size = (int(conf["HEIGHT"]), int(conf["WIDTH"]))
    maze = ones(size, int) * 15
    visited = zeros(size, int)
    perfect = bool(conf["PERFECT"].lower() != "false")
    if visited.shape[0] < 6 or visited.shape[1] < 8:
        is_42 = 0
        print("The '42' cannot be printed in a maze this size.")
    else:
        is_42 = 1
        hs = (visited.shape[0] - 1) // 2 - 2
        ws = (visited.shape[1] - 1) // 2 - 3
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
    current = [rng.randint(0, size[0] - 1), rng.randint(0, size[1] - 1)]
    visited[current[0]][current[1]] = 1
    """Algorithm"""
    algo = select_algo(conf)
    if algo == "AldousBroder":
        aldous_broder(maze, visited)
    elif algo == "DFS":
        dfs(maze, visited)
    elif algo == "Prim":
        prim(maze, visited)
    elif algo == "Wilson":
        wilson(maze, visited)
    else:
        print("Unknown or not implemented algorithm", file=stderr)
        return
    if perfect is False:
        imperfect(maze)
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


def handler(signum, frame):
    print("\rProgram terminated by user")
    exit(0)


if __name__ == "__main__":
    signal(SIGINT, handler)
    if len(argv) != 2:
        print("Only one configuration file is allowed", file=stderr)
    else:
        try:
            main()
        except MemoryError:
            print("[ERROR] Out of memory", file=stderr)
        except OverflowError:
            print(
                "[ERROR] Calculations exceed computer limits. "
                "Please, try lower maze size.", file=stderr
            )
        except KeyboardInterrupt:
            raise_signal(SIGINT)
