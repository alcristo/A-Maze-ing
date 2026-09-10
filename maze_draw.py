from maze_utils import get_walls, MazeOptions


"""Maze drawing module for a_maze_ing."""


def maze_draw(opts: MazeOptions) -> None:
    """Display the maze in terminal."""
    """with open(maze_file) as f:
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
    """

    file = opts._maze.split("\n\n")
    mazef = file[0].split("\n")
    maze = []
    w = 0
    for line in mazef:
        maze.append(line)
        if w == 0:
            w = len(line)
    rem = file[1].split("\n")
    en = rem[0].split(",")
    entry = (int(en[1]), int(en[0]))
    ex = rem[1].split(",")
    exit = (int(ex[1]), int(ex[0]))
    path = rem[2]
    pathtiles = []
    if opts._solution is True:
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

    print("\x1bc")
    for _ in range(2 * w + 1):
        print(f"{opts._palette['wall']}  {reset}", end="")
    print()
    h = len(maze)
    i = 0
    base = "0123456789abcdef"
    for i in range(h):
        row = maze[i]
        print(f"{opts._palette['wall']}  {reset}", end="")
        for j in range(w):
            c = row[j]
            if c == "f":
                print(f"{opts._palette['block']}  {reset}", end="")
            elif (i, j) == entry:
                print(f"{opts._palette['entry']}  {reset}", end="")
            elif (i, j) == exit:
                print(f"{opts._palette['exit']}  {reset}", end="")
            elif (i, j) in pathtiles and opts._solution is True:
                print(f"{opts._palette['path']}  {reset}", end="")
            else:
                print(f"{opts._palette['tile']}  {reset}", end="")
            if (i, j) in pathtiles and (i, j + 1) in pathtiles and get_walls(
                base.index(c)
            )[1] == 0:
                print(f"{opts._palette['path']}  {reset}", end="")
            elif get_walls(base.index(c))[1] == 0:
                print(f"{opts._palette['tile']}  {reset}", end="")
            else:
                print(f"{opts._palette['wall']}  {reset}", end="")
        print()
        print(f"{opts._palette['wall']}  {reset}", end="")
        for j in range(w):
            c = row[j]
            if (i, j) in pathtiles and (i + 1, j) in pathtiles and get_walls(
                base.index(c)
            )[2] == 0:
                print(f"{opts._palette['path']}  {reset}", end="")
            elif get_walls(base.index(c))[2] == 0:
                print(f"{opts._palette['tile']}  {reset}", end="")
            else:
                print(f"{opts._palette['wall']}  {reset}", end="")
            if i != range(h)[-1] and j != range(w)[-1]:
                p_path = [
                    get_walls(base.index(c))[1] == 0,
                    get_walls(base.index(c))[2] == 0,
                    get_walls(base.index(maze[i + 1][j]))[0] == 0,
                    get_walls(base.index(maze[i + 1][j]))[1] == 0,
                    get_walls(base.index(row[j + 1]))[2] == 0,
                    get_walls(base.index(row[j + 1]))[3] == 0
                ]
                if False not in p_path:
                    print(f"{opts._palette['tile']}  {reset}", end="")
                else:
                    print(f"{opts._palette['wall']}  {reset}", end="")
            else:
                print(f"{opts._palette['wall']}  {reset}", end="")
        print()
