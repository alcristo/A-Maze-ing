from maze_utils import get_walls, _MazeOptions
import sys
import termios
import tty
import time
# import json


class Player:
    def __init__(self, maze_file: str, opts: _MazeOptions) -> None:
        self._maze_file = maze_file
        self._opts = opts
        self._w = 0
        self._path = ""
        self._playable = False
        self.map()

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
            self._maze = maze
            en = f.readline().split(",")
            self._entry = (int(en[1]), int(en[0]))
            self._pos = self._entry
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
        print("=== A-Maze-ing ===")
        print("q. Quit")

    def move(self) -> str:
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

    def player_moves(self) -> None:
        base = "0123456789abcdef"
        self.print_map()
        # start_time = time.time()
        while self._playable is True:
            move = self.move()
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
            self.print_map()
            if move == "q":
                self._pos = (self._entry[0], self._entry[1])
                self._playable = False
                break
            elif self._pos == self._exit:
                """current_time = time.time() - start_time
                user = input("\x1b[KEnter user: ")
                t = float(current_time)
                with open("scores.json", "r") as f:
                    txt = f.read()
                    if txt == "":
                        scores: dict[str, float] = {}
                        break
                    scores = json.loads(txt)
                scores.update({user: round(t - start_time, 3)})
                j = json.dumps(scores)
                with open("scores.json", "w") as f:
                    f.write(j)
                print(
                    f"Your user has been saved as: {user} with",
                    f"{round(t - start_time, 3)} seconds"
                )
                time.sleep(10)"""
                self._pos = (self._entry[0], self._entry[1])
                self._playable = False
                return
            time.sleep(0.1)

    def show_player(self) -> None:
        self._playable = self._playable is False
