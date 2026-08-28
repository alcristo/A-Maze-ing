import sys
from numpy import zeros, ones
from maze_utils import MazeError, check_errors
from maze_algos import dfs, prim, wilson, aldous_broder, imperfect
from pathfinding import a_star
from maze_draw import maze_draw
from typing import Any
from functools import wraps
from collections.abc import Callable
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

    """Draw the maze"""
    maze_draw(conf["OUTPUT_FILE"])
    return conf['OUTPUT_FILE']


def handler(signum, frame):
    """Interruption signal handler (SIGINT, Ctrl+C)"""
    print("\rProgram terminated by user")
    exit()


def uint8(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Decorator to validate 0 <= value <= 255"""
    @wraps(func)
    def validate(*args: Any, **kwargs: Any) -> Any:
        if args[0] < 0 or args[0] > 255:
            raise ValueError
        return func(*args, **kwargs)
    return validate


@uint8
def validate_color(channel: int) -> None:
    pass


def select_color(palette: dict[str, str], key: str) -> None:
    print(f"Currently selected: {key}   {palette.get(key)}  \x1b[0m")
    try:
        R = int(input("Insert red (R) intensity [0-255]:   "))
        validate_color(R)
        G = int(input("Insert green (G) intensity [0-255]: "))
        validate_color(G)
        B = int(input("Insert blue (B) intensity [0-255]:  "))
        validate_color(B)
        palette.update({key: f"\x1b[48;2;{R};{G};{B}m"})
    except ValueError:
        print("[ERROR] Invalid color value. Aborting.")
        return


def change_colors(palette: dict[str, str]) -> None:
    reset = "\x1b[0m"
    old_pal = palette.copy()
    while True:
        print("== Change colors ==")
        print(f"1. Tile  {palette['tile']}  {reset}")
        print(f"2. Wall  {palette['wall']}  {reset}")
        print(f"3. Entry {palette['entry']}  {reset}")
        print(f"4. Exit  {palette['exit']}  {reset}")
        print(f"5. Path  {palette['path']}  {reset}")
        print(f"6. Block {palette['block']}  {reset}")
        print("d. Default palette")
        print("q. Quit palette selector")
        opt = input()
        if opt == "1":
            select_color(palette, "tile")
        elif opt == "2":
            select_color(palette, "wall")
        elif opt == "3":
            select_color(palette, "entry")
        elif opt == "4":
            select_color(palette, "exit")
        elif opt == "5":
            select_color(palette, "path")
        elif opt == "6":
            select_color(palette, "block")
        elif opt == "d":
            palette.update({"tile": "\x1b[47m"})
            palette.update({"wall": "\x1b[40m"})
            palette.update({"entry": "\x1b[45m"})
            palette.update({"exit": "\x1b[42m"})
            palette.update({"path": "\x1b[44m"})
            palette.update({"block": "\x1b[41m"})
        elif opt == "q":
            if palette == old_pal:
                return
            save = input("Save changes? Y/n   ")
            if save.lower() in ("", "y", "yes", "yea"):
                return
            if save.lower() in ("n", "no", "nay"):
                palette = old_pal.copy()
                del old_pal
                return
            else:
                print("Cancelling exit.")
        else:
            print("Incorrect input")
    return


def menu(maze: str) -> None:
    clear = "\x1bc"
    draw_path = False
    def_palette = {
        "tile": "\x1b[47m",
        "wall": "\x1b[40m",
        "entry": "\x1b[45m",
        "exit": "\x1b[42m",
        "path": "\x1b[44m",
        "block": "\x1b[41m"
    }
    palette = def_palette.copy()
    while True:
        print("=== A-Maze-ing ===")
        print("1. Generate a new maze")
        print("2. Show/hide solution")
        print("3. Change colors")
        print("q. Quit")
        opt = input("Select option: ")
        if opt == "1":
            print(f"{clear}")
            maze = generate(sys.argv[1])
            return menu(maze)
        elif opt == "2":
            draw_path = draw_path is False
            maze_draw(maze, draw_path, palette)
        elif opt == "3":
            change_colors(palette)
            maze_draw(maze, draw_path, palette)
        elif opt.lower() == "q":
            sys.exit()
        else:
            continue


if __name__ == "__main__":
    signal(SIGINT, handler)
    if len(sys.argv) != 2:
        print("Only one configuration file is allowed", file=sys.stderr)
    else:
        try:
            file = generate(sys.argv[1])
            menu(file)
        except MemoryError:
            print("[ERROR] Out of memory", file=sys.stderr)
        except OverflowError:
            print(
                "[ERROR] Calculations exceed computer limits. "
                "Please, try lower maze size.", file=sys.stderr
            )
        except KeyboardInterrupt:
            raise_signal(SIGINT)
