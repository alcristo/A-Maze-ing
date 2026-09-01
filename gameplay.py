from maze_utils import get_walls, _MazeOptions
import sys
import termios
import tty


class Player:
    def __init__(self, maze_file: str, opts: _MazeOptions) -> None:
        self._pos = opts._conf.get('ENTRY')
        self._maze_file = maze_file
        self._opts = opts
        self._playable = False

    def map(self) -> None:
        with open(self._maze_file) as f:
            line = f.readline()
            maze = []
            w = 0
            while line != "\n":
                maze.append(line.strip("\n"))
                if w == 0:
                    w = len(line) - 1
                line = f.readline()
            en = f.readline().split(",")
            entry = (int(en[1]), int(en[0]))
            ex = f.readline().split(",")
            exit = (int(ex[1]), int(ex[0]))
            path = f.readline()

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
            hex = "0"
            move = self.leer_tecla()
            walls = get_walls(base.index(hex))
            if move == "a":
                if walls[3] == 0:
                    print("west")
            elif move == "s":
                if walls[2] == 0:
                    print("south")
            elif move == "d":
                if walls[1] == 0:
                    print("east")
            elif move == "w":
                if walls[0] == 0:
                    print("north")

    def _show_player(self) -> None:
        self._playable = self._playable is False


player = Player()
player.ge