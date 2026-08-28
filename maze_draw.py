from maze_utils import get_walls


def maze_draw(
    maze_file: str,
    draw_path: bool = False,
    palette: dict[str, str] = {
        "tile": "\x1b[47m",
        "wall": "\x1b[40m",
        "entry": "\x1b[45m",
        "exit": "\x1b[42m",
        "path": "\x1b[44m",
        "block": "\x1b[41m"
    }
) -> None:
    with open(maze_file) as f:
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

    pathtiles = []
    if draw_path is True:
        curr = entry
        for dir in path:
            if dir == "N":
                curr = (curr[0] - 1, curr[1])
            elif dir == "S":
                curr = (curr[0] + 1, curr[1])
            elif dir == "W":
                curr = (curr[0], curr[1] - 1)
            elif dir == "E":
                curr = (curr[0], curr[1] + 1)
            else:
                break
            if curr == exit:
                break
            pathtiles.append(curr)
        pathtiles.append(exit)
        pathtiles.insert(0, entry)

    reset = "\x1b[0m"
    """palette = {
        "tile": "\x1b[47m",
        "wall": "\x1b[40m",
        "entry": "\x1b[45m",
        "exit": "\x1b[42m",
        "path": "\x1b[44m",
        "block": "\x1b[41m"
    }"""
    """black = "\x1b[40m"
    red = "\x1b[41m"
    green = "\x1b[42m"
    # yellow = "\x1b[43m"
    blue = "\x1b[44m"
    magenta = "\x1b[45m"
    # cyan = "\x1b[46m"
    white = "\x1b[47m"
    """

    """reset = "\x1b[0m"
    black = "\x1b[48;2;0;0;0m"
    red = "\x1b[48;2;255;0;0m"
    green = "\x1b[48;2;0;255;0m"
    # yellow = "\x1b[48;2;255;255;0m"
    blue = "\x1b[48;2;0;0;255m"
    magenta = "\x1b[48;2;255;0;255m"
    # cyan = "\x1b[448;2;0;255;255m"
    white = "\x1b[48;2;255;255;255m"
"""

    print("\x1bc")
    for _ in range(2 * w + 1):
        print(f"{palette['wall']}  {reset}", end="")
    print()
    h = len(maze)
    i = 0
    base = "0123456789abcdef"
    for i in range(h):
        row = maze[i]
        print(f"{palette['wall']}  {reset}", end="")
        for j in range(w):
            c = row[j]
            if c == "f":
                print(f"{palette['block']}  {reset}", end="")
            elif (i, j) == entry:
                print(f"{palette['entry']}  {reset}", end="")
            elif (i, j) == exit:
                print(f"{palette['exit']}  {reset}", end="")
            elif (i, j) in pathtiles and draw_path is True:
                print(f"{palette['path']}  {reset}", end="")
            else:
                print(f"{palette['tile']}  {reset}", end="")
            if (i, j) in pathtiles and (i, j + 1) in pathtiles and get_walls(
                base.index(c)
            )[1] == 0:
                print(f"{palette['path']}  {reset}", end="")
            elif get_walls(base.index(c))[1] == 0:
                print(f"{palette['tile']}  {reset}", end="")
            else:
                print(f"{palette['wall']}  {reset}", end="")
        print()
        print(f"{palette['wall']}  {reset}", end="")
        for j in range(w):
            c = row[j]
            if (i, j) in pathtiles and (i + 1, j) in pathtiles and get_walls(
                base.index(c)
            )[2] == 0:
                print(f"{palette['path']}  {reset}", end="")
            elif get_walls(base.index(c))[2] == 0:
                print(f"{palette['tile']}  {reset}", end="")
            else:
                print(f"{palette['wall']}  {reset}", end="")
            print(f"{palette['wall']}  {reset}", end="")
        print()
