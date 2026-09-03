from numpy import zeros, ones
from maze_utils import MazeError, check_errors, _MazeOptions
from maze_algos import dfs, prim, wilson, aldous_broder, imperfect
from pathfinding import a_star
from maze_draw import maze_draw
from gameplay import Player
import sys
import random
import time
from typing import Any
from signal import SIGINT, signal, raise_signal


def select_algo(conf: dict[str, str]) -> str:
    """Return selected algorithm string"""
    try:
        if conf["ALGORITHM"].lower() in (
            "aldous broder", "aldousbroder", "aldous_broder", "aldous-broder",
            "ab"
        ):
            return "AldousBroder"
        elif conf["ALGORITHM"].lower() in (
            "dfs", "depthfirstsearch", "depth first search",
            "depth_first_search",
            "recursivebacktracker", "recursive backtracker",
            "recursive_backtracker", "rb"
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


def generate(opts: _MazeOptions, conf: dict[str, str]) -> str:

    """Create the maze and visited tiles arrays"""
    size = (int(conf["HEIGHT"]), int(conf["WIDTH"]))
    maze = ones(size, int) * 15
    visited = zeros(size, int)
    perfect = bool(conf["PERFECT"].lower() != "false")
    if visited.shape[0] < 7 or visited.shape[1] < 9:
        print("The '42' cannot be printed in a maze this size.")
        time.sleep(3)
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
        aldous_broder(maze, visited, opts)
    elif algo == "DFS":
        dfs(maze, visited, opts)
    elif algo == "Prim":
        prim(maze, visited, opts)
    elif algo == "Wilson":
        wilson(maze, visited, opts)
    else:
        print("Unknown or not implemented algorithm", file=sys.stderr)
        sys.exit()
    if perfect is False:
        imperfect(maze, opts)
    """Solution"""
    start = conf["ENTRY"].split(",")
    end = conf["EXIT"].split(",")
    entr = (int(start[1]), int(start[0]))
    exit = (int(end[1]), int(end[0]))
    sol = a_star(maze, entr, exit)

    """Save the file"""
    base = "0123456789abcdef"
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


def change_colors(maze: str, opts: _MazeOptions) -> None:
    reset = "\x1b[0m"
    old_pal = opts._palette.copy()
    while True:
        print("\x1b[H\x1b[0J", end="")
        maze_draw(maze, opts)
        print("== Change colors ==")
        print(f"1. Tile   {opts._palette['tile']}  {reset}")
        print(f"2. Wall   {opts._palette['wall']}  {reset}")
        print(f"3. Entry  {opts._palette['entry']}  {reset}")
        print(f"4. Exit   {opts._palette['exit']}  {reset}")
        print(f"5. Path   {opts._palette['path']}  {reset}")
        print(f"6. Block  {opts._palette['block']}  {reset}")
        print(f"7. Player {opts._palette['player']}  {reset}")
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
        elif opt == "7":
            opts._select_color("player")
        elif opt == "d":
            opts._palette.update({"tile": "\x1b[47m"})
            opts._palette.update({"wall": "\x1b[40m"})
            opts._palette.update({"entry": "\x1b[45m"})
            opts._palette.update({"exit": "\x1b[42m"})
            opts._palette.update({"path": "\x1b[44m"})
            opts._palette.update({"block": "\x1b[41m"})
            opts._palette.update({"player": "\x1b[46m"})
        elif opt == "q":
            if opts._palette == old_pal:
                return
            save = input("Save changes? (Y/n)   ")
            if save.lower() in ("", "y", "yes", "yea", "yup"):
                return
            if save.lower() in ("n", "no", "nay", "nope"):
                opts._palette = old_pal.copy()
                del old_pal
                return
            else:
                print("Cancelling exit.")
        else:
            pass


def change_config(maze: str, opts: _MazeOptions) -> None:
    old_conf = opts._conf.copy()
    while True:
        print("\x1b[H\x1b[0J", end="")
        maze_draw(maze, opts)
        print("== Change configuration ==")
        print(f"1. Height:      {opts._conf.get('HEIGHT')}")
        print(f"2. Width:       {opts._conf.get('WIDTH')}")
        print(f"3. Entry:       {opts._conf.get('ENTRY')}")
        print(f"4. Exit:        {opts._conf.get('EXIT')}")
        print(f"5. Perfect:     {opts._conf.get('PERFECT')}")
        print(f"6. Output file: {opts._conf.get('OUTPUT_FILE')}")
        print(f"7. Seed:        {opts._conf.get('SEED')}")
        print(f"8. Algorithm:   {opts._conf.get('ALGORITHM')}")
        print(f"9. Animation:   {opts._conf.get('ANIMATE')}")
        print("d. Default playable maze")
        print("u. Undo changes")
        print("q. Quit configuration selector")
        try:
            h, w = int(opts._conf["HEIGHT"]), int(opts._conf["WIDTH"])
            if (
                opts._conf["ANIMATE"].lower() == "true" and (
                    h > 60 or h * w > 1000)
            ):
                raise MazeError("Maze is too big for a smooth animation")
            check_errors(opts._conf)
        except MazeError as e:
            print(e)
        opt = input("\x1b[KSelect option: ")
        if opt == "1":
            opts._select_config("HEIGHT")
        elif opt == "2":
            opts._select_config("WIDTH")
        elif opt == "3":
            opts._select_config("ENTRY")
        elif opt == "4":
            opts._select_config("EXIT")
        elif opt == "5":
            opts._select_config("PERFECT")
        elif opt == "6":
            opts._select_config("OUTPUT_FILE")
        elif opt == "7":
            opts._select_config("SEED")
        elif opt == "8":
            opts._select_config("ALGORITHM")
        elif opt == "9":
            opts._select_config("ANIMATE")
        elif opt.lower() == "d":
            opts._conf = {
                "HEIGHT": "15",
                "WIDTH": "31",
                "ENTRY": "0,7",
                "EXIT": "30,7",
                "PERFECT": "False",
                "OUTPUT_FILE": "default_maze.txt",
                "SEED": "alcristo",
                "ALGORITHM": "Wilson",
                "ANIMATE": "True"
            }
        elif opt.lower() == "u":
            opts._conf = old_conf.copy()
        elif opt.lower() == "q":
            if opts._conf == old_conf:
                return
            try:
                h, w = int(opts._conf["HEIGHT"]), int(opts._conf["WIDTH"])
                if (
                    opts._conf["ANIMATE"].lower() == "true" and (
                        h > 60 or h * w > 1000)
                ):
                    raise MazeError("Maze is too big for a smooth animation")
                check_errors(opts._conf)
            except MazeError as e:
                print(e.msg)
                continue
            save = input("Save changes? (Y/n)   ")
            if save.lower() in ("", "y", "yes", "yea", "yup"):
                return
            if save.lower() in ("n", "no", "nay", "nope"):
                opts._conf = old_conf.copy()
                del old_conf
                return
            else:
                pass
        else:
            pass


def players_stats(maze: str, opts: _MazeOptions) -> None:
    with open("scores.json", "r", encoding="utf-8") as f:
        content = f.read()
    maze_draw(maze, opts)
    print(content)
    char = input("Press q to quit   ")
    while char != "q":
        maze_draw(maze, opts)
        print(content)
        char = input("Press q to quit: ")
        # continue


def menu(maze: str, opts: _MazeOptions) -> None:
    clear = "\x1bc"
    player = Player(maze, opts)
    while True:
        print("\x1b[H\x1b[J", end="")
        maze_draw(maze, opts)
        print("=== A-Maze-ing ===")
        print("1. Generate a new maze")
        print("2. Show/hide solution")
        print("3. Change colors")
        print("4. Change configuration")
        print("5. Play")
        # print("6. Top players")
        print("q. Quit")
        opt = input("\x1b[KSelect option: ")
        if opt == "1":
            print(f"{clear}")
            maze = generate(opts, opts._conf)
            player = Player(maze, opts)
            # with open("scores.json", "w"):
            #     pass
            # return menu(maze, opts)
        elif opt == "2":
            opts._show_hide()
        elif opt == "3":
            change_colors(maze, opts)
        elif opt == "4":
            change_config(maze, opts)
        elif opt == "5":
            player.show_player()
        # elif opt == "6":
            # players_stats(maze, opts)
        elif opt.lower() == "q":
            sys.exit()
        else:
            pass
        player.player_moves()


def maze_config(conf_file: str) -> dict[str, str]:
    """Open the configuration file and set everything"""
    with open(conf_file) as f:
        txt = f.read()
        opts = txt.split("\n")
        tup = [
            tuple(i.split("=")) for i in opts if "=" in i and i.count("=") == 1
        ]
        conf = {i[0].upper(): i[1] for i in tup if i[0][0] != "#"}
    check_errors(conf)
    if str(conf.get("PERFECT")).lower() not in ("true", "false"):
        conf.update({"PERFECT": "True"})
    valid_algos = (
        "wilson", "prim", "dfs", "ab", "aldous broder", "aldousbroder", "rb",
        "aldous_broder", "aldous-broder", "depth first search",
        "depthfirstserach", "depth_first_search", "recursivebacktracker",
        "recursive backtracker", "recursive_backtracker"
    )
    if str(conf.get("ALGORITHM")).lower() not in valid_algos:
        conf.update({"ALGORITHM": "Prim"})
    if str(conf.get("ANIMATE")).lower() not in ("true", "false"):
        conf.update({"ANIMATE": "False"})
    return conf


def init_config() -> dict[str, str]:
    while True:
        conf: dict[str, str] = {}
        try:
            h = input(
                f"Enter maze height (int > 0); current {conf.get('HEIGHT')}: "
            )
            if h == "" and conf.get("HEIGHT") is not None:
                he = int(conf["HEIGHT"])
            elif conf.get("HEIGHT") is None or conf.get("HEIGHT") != h:
                he = int(h)
                assert he > 0
                conf.update({"HEIGHT": h})
            if he > 60:
                print("Maze is too high. Animation will be disabled.")
                conf.update({"ANIMATE": "False"})
            w = input(
                f"Enter maze width (int > 0); current {conf.get('WIDTH')}: "
            )
            if w == "" and conf.get("WIDTH") is not None:
                wi = int(conf["WIDTH"])
            elif conf.get("WIDTH") is None or conf.get("WIDTH") != w:
                wi = int(w)
                assert wi > 0
                conf.update({"WIDTH": w})
            if he * wi > 151**2:
                print("Maze is too big; maze generation cancelled")
                continue
            elif he * wi > 31**2:
                print("Maze is big; animation will be disabled")
                conf.update({"ANIMATE": "False"})
            en = input(
                "Enter maze entry (0 ≤ x,y < width,height); "
                f"current {conf.get('ENTRY')}: "
            )
            if en == "" and conf.get("ENTRY") is not None:
                pass
            elif conf.get("ENTRY") is None or conf.get("ENTRY") != en:
                ent = en.split(",")
                entry = (int(ent[0]), int(ent[1]))
                conds = (
                    entry[0] >= 0, entry[0] < he, entry[1] >= 0, entry[1] < wi
                )
                assert [i for i in conds]
                conf.update({"ENTRY": en})
            ex = input(
                "Enter maze exit (0 ≤ x,y < width,height); "
                f"current {conf.get('EXIT')}: "
            )
            if ex == "" and conf.get("EXIT") is not None:
                pass
            elif conf.get("EXIT") is None or conf.get("EXIT") != ex:
                assert en != ex
                exi = ex.split(",")
                ext = (int(exi[0]), int(exi[1]))
                conds = (ext[0] >= 0, ext[0] < he, ext[1] >= 0, ext[1] < wi)
                assert [i for i in conds]
                conf.update({"EXIT": ex})
        except ValueError as e:
            print(e)
            continue
        except AssertionError:
            print("The displayed condition is not satisfied")
            continue
        except IndexError as e:
            print(e)
            continue
        try:
            check_errors(conf)
            break
        except MazeError as e:
            print(e.msg)
            continue
    perfect = input("Print a perfect maze? (Y/n): ")
    if perfect.lower() in ("n", "no", "nay", "nope"):
        conf.update({"PERFECT": "False"})
    else:
        conf.update({"PERFECT": "True"})
    out = input("Enter the maze output file (default: maze.txt): ")
    if out == "":
        conf.update({"OUTPUT_FILE": "maze.txt"})
    else:
        conf.update({"OUTPUT_FILE": out})
    seed = input("Enter the maze seed (leave in blank for random): ")
    if seed != "":
        conf.update({"SEED": seed})
    valid_algos = (
        "wilson", "prim", "dfs", "ab", "aldous broder", "aldousbroder", "rb",
        "aldous_broder", "aldous-broder", "depth first search",
        "depthfirstserach", "depth_first_search", "recursivebacktracker",
        "recursive backtracker", "recursive_backtracker"
    )
    while True:
        print(
            "Enter the maze generation algorithm "
            "(Depth First Search/Recursive Backtracker, Prim, Wilson, "
            "Aldous-Broder; defaults to Prim): "
        )
        algo = input()
        if algo == "":
            break
        try:
            assert algo.lower() in valid_algos
            conf.update({"ALGORITHM": algo})
            break
        except AssertionError:
            print("Invalid algorithm")
            continue
    if conf.get("ANIMATE") is not None:
        animate = input("Animate the maze generation? (y/N): ")
        if animate.lower() in ("y", "yes", "yea", "yup"):
            conf.update({"ANIMATE": "True"})
        else:
            conf.update({"ANIMATE": "False"})
    return conf


def handler(signum: Any, frame: Any) -> None:
    """Interruption signal handler (SIGINT, Ctrl+C)"""
    print("\nProgram terminated by user")
    exit()


if __name__ == "__main__":
    signal(SIGINT, handler)
    if len(sys.argv) > 2:
        print("Only one configuration file is allowed", file=sys.stderr)
    try:
        try:
            conf = maze_config(sys.argv[1])
            """opts = _MazeOptions(conf)
            file = generate(opts, opts._conf)
            maze_draw(file, opts)"""
        except IndexError:
            conf = init_config()
            """opts = _MazeOptions(conf)
            file = generate(opts, opts._conf)
            maze_draw(file, opts)"""
        except FileNotFoundError:
            conf = init_config()
            """opts = _MazeOptions(conf)
            file = generate(opts, opts._conf)
            maze_draw(file, opts)"""
        except MazeError as e:
            print(e.msg)
            time.sleep(3)
            conf = init_config()
        opts = _MazeOptions(conf)
        file = generate(opts, opts._conf)
        maze_draw(file, opts)
        menu(file, opts)
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
