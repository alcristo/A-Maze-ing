from maze_utils import get_walls, _MazeOptions
import sys
import termios
import tty


class Player:
    def __init__(self, maze_file: str, opts: _MazeOptions) -> None:
        self._maze_file = maze_file
        self._opts = opts
        self._maze = []
        self._w = 0
        self._exit = 0
        self._path = ""
        self._playable = False
        self.map()
        self._pos = self._entry

    def map(self) -> None:
        with open(self._maze_file) as f:
            line = f.readline()
            maze = []
            w = 0
            while line != "\n":
                maze.append(line.strip("\n"))
                if w == 0:
                    self._w = len(line) - 1
                line = f.readline()
            self.set_maze(maze)
            en = f.readline().split(",")
            self._entry = (int(en[1]), int(en[0]))
            ex = f.readline().split(",")
            self._exit = (int(ex[1]), int(ex[0]))

    def print_map(self) -> None:
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

    def leer_tecla(self) -> str:
        fd = sys.stdin.fileno()
        config_antigua = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            tecla = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, config_antigua)
        return tecla

    def player_moves(self) -> None:
        base = "0123456789abcdef"
        while self._playable is True:
            move = self.leer_tecla()
            walls = get_walls(
                base.index(self._maze[self._pos[0]][self._pos[1]]))
            if move == "a":
                if walls[3] == 0:
                    self._pos = (self._pos[0], self._pos[1] - 1)
            elif move == "s":
                if walls[2] == 0:
                    self._pos = (self._pos[0] + 1, self._pos[1])
            elif move == "d":
                if walls[1] == 0:
                    self._pos = (self._pos[0], self._pos[1] + 1)
            elif move == "w":
                if walls[0] == 0:
                    self._pos = (self._pos[0] - 1, self._pos[1])
            self.print_map()
            if self._pos == self._exit or move == "q":
                self._pos = self._entry
                self._playable = False
                break

    def set_maze(self, maze: list) -> None:
        self._maze = maze

    def show_player(self) -> None:
        self._playable = self._playable is False
