from maze_utils import get_walls, MazeOptions
import sys
import termios
import tty
import time


"""Module for a_maze_ing "play" mode."""


class Player:
    """Player class for "play" mode."""

    def __init__(self, opts: MazeOptions) -> None:
        """Initialize a player.

        Arguments:
            maze_file: the file containing the maze with entry and exit tiles.
            opts: the maze configuration, containing the display colors.
        """
        self._maze_file = opts._conf.get("OUTPUT_FILE")
        self._opts = opts
        self._w = 0
        self._path = ""
        self._playable = False
        self._map()

    def _map(self) -> None:
        """Read maze file"""
        with open(self._maze_file) as f:
            line = f.readline()
            maze = []
            w = 0
            while line != "\n":
                maze.append(line.strip("\n"))
                if w == 0:
                    self._w = len(line) - 1
                line = f.readline()
            self._maze = maze
            en = f.readline().split(",")
            self._entry = (int(en[1]), int(en[0]))
            self._pos = self._entry
            ex = f.readline().split(",")
            self._exit = (int(ex[1]), int(ex[0]))

    def _print_map(self) -> None:
        """Display maze in terminal with player."""
        reset = "\x1b[0m"
        print("\x1bc")
        for _ in range(2 * self._w + 1):
            print(f"{self._opts._palette['wall']}  {reset}", end="")
        print()
        h = len(self._maze)
        i = 0
        base = "0123456789abcdef"
        for i in range(h):
            row = self._maze[i]
            print(f"{self._opts._palette['wall']}  {reset}", end="")
            for j in range(self._w):
                c = row[j]
                if c == "f":
                    print(f"{self._opts._palette['block']}  {reset}", end="")
                elif (i, j) == self._pos:
                    print(f"{self._opts._palette['player']}  {reset}", end="")
                elif (i, j) == self._entry:
                    print(f"{self._opts._palette['entry']}  {reset}", end="")
                elif (i, j) == self._exit:
                    print(f"{self._opts._palette['exit']}  {reset}", end="")
                else:
                    print(f"{self._opts._palette['tile']}  {reset}", end="")
                if get_walls(base.index(c))[1] == 0:
                    print(f"{self._opts._palette['tile']}  {reset}", end="")
                else:
                    print(f"{self._opts._palette['wall']}  {reset}", end="")
            print()
            print(f"{self._opts._palette['wall']}  {reset}", end="")
            for j in range(self._w):
                c = row[j]
                if get_walls(base.index(c))[2] == 0:
                    print(f"{self._opts._palette['tile']}  {reset}", end="")
                else:
                    print(f"{self._opts._palette['wall']}  {reset}", end="")
                if i != range(h)[-1] and j != range(self._w)[-1]:
                    p_path = [
                        get_walls(base.index(c))[1] == 0,
                        get_walls(base.index(c))[2] == 0,
                        get_walls(base.index(self._maze[i + 1][j]))[0] == 0,
                        get_walls(base.index(self._maze[i + 1][j]))[1] == 0,
                        get_walls(base.index(row[j + 1]))[2] == 0,
                        get_walls(base.index(row[j + 1]))[3] == 0
                    ]
                    if False not in p_path:
                        print(
                            f"{self._opts._palette['tile']}  {reset}", end=""
                        )
                    else:
                        print(
                            f"{self._opts._palette['wall']}  {reset}", end=""
                        )
                else:
                    print(f"{self._opts._palette['wall']}  {reset}", end="")
            print()
        print("=== A-Maze-ing ===")
        print("q. Quit")

    def _move(self) -> str:
        """Analyze user input, return string."""
        fd = sys.stdin.fileno()
        old_config = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            order = sys.stdin.read(1)
            if order == "\x1b":
                order += sys.stdin.read(2)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_config)
        return order

    def _player_moves(self) -> None:
        """Move the player through the maze."""
        base = "0123456789abcdef"
        self._print_map()
        while self._playable is True:
            move = self._move()
            walls = get_walls(
                base.index(self._maze[self._pos[0]][self._pos[1]])
            )
            if move in ("a", "\x1b[D"):
                if walls[3] == 0:
                    self._pos = (self._pos[0], self._pos[1] - 1)
            elif move in ("s", "\x1b[B"):
                if walls[2] == 0:
                    self._pos = (self._pos[0] + 1, self._pos[1])
            elif move in ("d", "\x1b[C"):
                if walls[1] == 0:
                    self._pos = (self._pos[0], self._pos[1] + 1)
            elif move in ("w", "\x1b[A"):
                if walls[0] == 0:
                    self._pos = (self._pos[0] - 1, self._pos[1])
            self._print_map()
            if move == "q":
                self._pos = (self._entry[0], self._entry[1])
                self._playable = False
                break
            elif self._pos == self._exit:
                self._pos = (self._entry[0], self._entry[1])
                self._playable = False
                return
            time.sleep(0.1)

    def _show_player(self) -> None:
        """Show or hide the player"""
        self._playable = self._playable is False
