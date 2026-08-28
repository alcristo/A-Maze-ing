from numpy import zeros, ones
from maze_utils import MazeError, check_errors, _MazeOptions
from maze_algos import dfs, prim, wilson, aldous_broder, imperfect
from pathfinding import a_star
from maze_draw import maze_draw
import sys
import random
from typing import Any
from signal import SIGINT, signal, raise_signal


def select_algo(conf: dict[str, str]) -> str:
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


def generate(conf_file: str) -> str:
    """Open the configuration file and set everything"""
    with open(conf_file) as f:
        txt = f.read()
        opts = txt.split("\n")
        tup = [tuple(i.split("=")) for i in opts if "=" in i]
        conf = {i[0].upper(): i[1] for i in tup if i[0][0] != "#"}
    try:
        check_errors(conf)
    except MazeError as e:
        print(e.msg, file=sys.stderr)
        sys.exit()

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
        print("Unknown or not implemented algorithm", file=sys.stderr)
        sys.exit()
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
    return conf['OUTPUT_FILE']


def change_colors(opts: _MazeOptions) -> None:
    reset = "\x1b[0m"
    old_pal = opts._palette.copy()
    print("\x1b[s")
    while True:
        print("\x1b[u\x1b[1A\x1b[0J")
        print("== Change colors ==")
        print(f"1. Tile  {opts._palette['tile']}  {reset}")
        print(f"2. Wall  {opts._palette['wall']}  {reset}")
        print(f"3. Entry {opts._palette['entry']}  {reset}")
        print(f"4. Exit  {opts._palette['exit']}  {reset}")
        print(f"5. Path  {opts._palette['path']}  {reset}")
        print(f"6. Block {opts._palette['block']}  {reset}")
        print("d. Default palette")
        print("q. Quit palette selector")
        opt = input("\x1b[KSelect option: ")
        if opt == "1":
            opts._select_color("tile")
        elif opt == "2":
            opts._select_color("wall")
        elif opt == "3":
            opts._select_color("entry")
        elif opt == "4":
            opts._select_color("exit")
        elif opt == "5":
            opts._select_color("path")
        elif opt == "6":
            opts._select_color("block")
        elif opt == "d":
            opts._palette.update({"tile": "\x1b[47m"})
            opts._palette.update({"wall": "\x1b[40m"})
            opts._palette.update({"entry": "\x1b[45m"})
            opts._palette.update({"exit": "\x1b[42m"})
            opts._palette.update({"path": "\x1b[44m"})
            opts._palette.update({"block": "\x1b[41m"})
        elif opt == "q":
            if opts._palette == old_pal:
                return
            save = input("Save changes? Y/n   ")
            if save.lower() in ("", "y", "yes", "yea", "yup"):
                return
            if save.lower() in ("n", "no", "nay", "nope"):
                opts._palette = old_pal.copy()
                del old_pal
                print("\x1b[u\x1b[0J")
                return
            else:
                print("Cancelling exit.")
        else:
            print("Incorrect input")
    return


def menu(maze: str, opts: _MazeOptions = _MazeOptions()) -> None:
    clear = "\x1bc"
    while True:
        # print("\x1b[s")
        print("=== A-Maze-ing ===")
        print("1. Generate a new maze")
        print("2. Show/hide solution")
        print("3. Change colors")
        print("q. Quit")
        opt = input("\x1b[KSelect option: ")
        if opt == "1":
            print(f"{clear}")
            maze = generate(sys.argv[1])
            maze_draw(maze, opts)
            return menu(maze, opts)
        elif opt == "2":
            opts._show_hide()
            maze_draw(maze, opts)
        elif opt == "3":
            print("\x1b[7F\x1bJ")
            change_colors(opts)
            maze_draw(maze, opts)
        elif opt.lower() == "q":
            sys.exit()
        else:
            print("\x1b[7F\x1bJ")


def handler(signum: Any, frame: Any) -> None:
    """Interruption signal handler (SIGINT, Ctrl+C)"""
    print("\nProgram terminated by user")
    exit()


if __name__ == "__main__":
    signal(SIGINT, handler)
    if len(sys.argv) != 2:
        print("Only one configuration file is allowed", file=sys.stderr)
    else:
        try:
            file = generate(sys.argv[1])
            maze_draw(file)
            menu(file)
        except MemoryError:
            print("[ERROR] Out of memory", file=sys.stderr)
        except OverflowError:
            print(
                "[ERROR] Calculations exceed computer limits. "
                "Please, try lower maze size.", file=sys.stderr
            )
        except EOFError:
            print("\nProgram terminated by user")
        except KeyboardInterrupt:
            raise_signal(SIGINT)
