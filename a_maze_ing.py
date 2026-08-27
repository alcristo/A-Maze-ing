from sys import argv, stderr, exit
from numpy import zeros, ones
from maze_utils import MazeError, check_errors
from maze_algos import dfs, prim, wilson, aldous_broder, imperfect
from pathfinding import a_star
from maze_draw import maze_draw
import random
from signal import SIGINT, signal, raise_signal


def select_algo(conf: dict) -> str:
    """Return selected algorithm string"""
    try:
        if conf["ALGORITHM"].lower() in (
            "aldous broder", "aldousbroder", "aldous_broder", "aldous-broder"
        ):
            return "AldousBroder"
        elif conf["ALGORITHM"].lower() in (
            "dfs", "depthfirstsearch", "depth first search",
            "depth_first_search",
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
        tup = [tuple(i.split("=")) for i in opts if "=" in i]
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
    if visited.shape[0] < 7 or visited.shape[1] < 9:
        print("The '42' cannot be printed in a maze this size.")
    else:
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
        for tile in pos_42:
            visited[tile[0]][tile[1]] = -1

    """Algorithm"""
    random.seed(conf.get("SEED"))
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
    entr = (int(start[1]), int(start[0]))
    exit = (int(end[1]), int(end[0]))
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
        out.write(f"{entr[1]},{entr[0]}\n")
        out.write(f"{exit[1]},{exit[0]}\n")
        out.write(sol)

    """Draw the maze"""
    maze_draw(conf["OUTPUT_FILE"])


def handler(signum, frame):
    """Interruption signal handler (SIGINT, Ctrl+C)"""
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
