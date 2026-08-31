from numpy.typing import NDArray
from typing import Any
from functools import wraps
from collections.abc import Callable


class MazeError(Exception):
    def __init__(self, msg: str = ""):
        self.msg = msg


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


class _MazeOptions:
    def __init__(self, conf: dict[str, str]) -> None:
        self._conf = conf
        self._solution = False
        self._palette = {
            "tile": "\x1b[47m",
            "wall": "\x1b[40m",
            "entry": "\x1b[45m",
            "exit": "\x1b[42m",
            "path": "\x1b[44m",
            "block": "\x1b[41m"
        }

    def _show_hide(self) -> None:
        self._solution = self._solution is False

    @staticmethod
    def _uint8(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        """Decorator to validate 0 <= value <= 255"""
        @wraps(func)
        def validate(*args: Any, **kwargs: Any) -> Any:
            if args[0] < 0 or args[0] > 255:
                raise ValueError
            return func(*args, **kwargs)
        return validate

    @staticmethod
    @_uint8
    def _validate_color(channel: int) -> None:
        pass

    def _select_color(self, key: str) -> None:
        if key not in self._palette.keys():
            print("Option not in palette.")
            return
        print(f"Currently selected: {key} {self._palette.get(key)}  \x1b[0m")
        try:
            R = int(input("Insert red (R) intensity [0-255]:   "))
            validate_color(R)
            G = int(input("Insert green (G) intensity [0-255]: "))
            validate_color(G)
            B = int(input("Insert blue (B) intensity [0-255]:  "))
            validate_color(B)
            self._palette.update({key: f"\x1b[48;2;{R};{G};{B}m"})
        except ValueError:
            print("[ERROR] Invalid color value. Aborting.")
            return

    def _select_config(self, key: str) -> None:
        he = int(self._conf["HEIGHT"])
        wi = int(self._conf["WIDTH"])
        if key == "HEIGHT":
            try:
                h = input(
                    f"New maze height (current {self._conf.get('HEIGHT')}): "
                )
                he = int(h)
                if h == "":
                    return
                assert he > 0
                self._conf.update({"HEIGHT": h})
            except ValueError as e:
                print(e)
                return
            except AssertionError:
                print("Height must be positive")
                return
        elif key == "WIDTH":
            try:
                w = input(
                    f"New maze width (current {self._conf.get('WIDTH')}): "
                )
                if w == "":
                    return
                assert wi > 0
                self._conf.update({"WIDTH": w})
            except ValueError as e:
                print(e)
                return
            except AssertionError:
                print("Width must be positive")
                return
        elif key == "ENTRY":
            en = input(
                "New maze entry (0 ≤ x,y < width,height); "
                f"(current {self._conf.get('ENTRY')}): "
            )
            if en == "":
                return
            try:
                ent = en.split(",")
                entry = (int(ent[0]), int(ent[1]))
                conds = (
                    entry[0] >= 0, entry[0] < he, entry[1] >= 0, entry[1] < wi
                )
                assert [i for i in conds]
                self._conf.update({"ENTRY": en})
            except ValueError as e:
                print(e)
                return
            except IndexError as e:
                print(e)
                return
            except AssertionError:
                print("Entry must be in bounds")
        elif key == "EXIT":
            ex = input(
                "New maze exit (0 ≤ x,y < width,height); "
                f"(current {self._conf.get('EXIT')}): "
            )
            if ex == "":
                return
            try:
                exi = ex.split(",")
                ext = (int(exi[0]), int(exi[1]))
                conds = (ext[0] >= 0, ext[0] < he, ext[1] >= 0, ext[1] < wi)
                assert [i for i in conds]
                self._conf.update({"EXIT": ex})
            except ValueError as e:
                print(e)
                return
            except IndexError as e:
                print(e)
                return
            except AssertionError:
                print("Exit must be in bounds")
                return
        elif key == "PERFECT":
            perfect = input("Print a perfect maze? (Y/n): ")
            if perfect.lower() in ("n", "no", "nay", "nope"):
                self._conf.update({"PERFECT": "False"})
            else:
                self._conf.update({"PERFECT": "True"})
        elif key == "OUTPUT_FILE":
            out = input("New maze output file (default: maze.txt): ")
            if out == "":
                self._conf.update({"OUTPUT_FILE": "maze.txt"})
            else:
                self._conf.update({"OUTPUT_FILE": out})
        elif key == "SEED":
            seed = input("Enter the maze seed (leave in blank for random): ")
            if seed != "":
                self._conf.update({"SEED": seed})
            else:
                if self._conf.get("SEED") is not None:
                    self._conf.pop("SEED")
        elif key == "ALGORITHM":
            valid_algos = (
                "wilson", "prim", "dfs", "ab", "aldous broder", "aldousbroder",
                "rb", "aldous_broder", "aldous-broder", "depth first search",
                "depthfirstserach", "depth_first_search",
                "recursivebacktracker", "recursive backtracker",
                "recursive_backtracker"
            )
            print(
                "Enter the maze generation algorithm "
                "(Depth First Search/Recursive Backtracker, Prim, Wilson, "
                "Aldous-Broder; defaults to Prim): "
            )
            algo = input()
            if algo == "":
                return
            try:
                assert algo.lower() in valid_algos
                self._conf.update({"ALGORITHM": algo})
            except AssertionError:
                print("Invalid algorithm")
                return


def manhattan(curr: tuple[int, int], neigh: tuple[int, int]) -> int:
    """Manhattan heuristic, return distance"""
    return abs(curr[0] - neigh[0]) + abs(curr[1] - neigh[1])


def check_errors(conf: dict[str, str]) -> None:
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


def check_tile(maze: NDArray[Any], coords: tuple[int, int]) -> None:
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
