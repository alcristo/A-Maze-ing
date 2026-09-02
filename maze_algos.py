from numpy.typing import NDArray
import random as rng
from typing import Any
from maze_utils import manhattan, get_walls, _MazeOptions
from pathfinding import a_star
import time


def creation_draw(
        maze_file: str, opts: _MazeOptions) -> None:
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
            else:
                print(f"{opts._palette['tile']}  {reset}", end="")
            if get_walls(base.index(c))[1] == 0:
                print(f"{opts._palette['tile']}  {reset}", end="")
            else:
                print(f"{opts._palette['wall']}  {reset}", end="")
        print()
        print(f"{opts._palette['wall']}  {reset}", end="")
        for j in range(w):
            c = row[j]
            if get_walls(base.index(c))[2] == 0:
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


def write_path(maze: NDArray[Any], opts: _MazeOptions) -> None:
    size = (int(opts._conf["HEIGHT"]), int(opts._conf["WIDTH"]))
    start = opts._conf["ENTRY"].split(",")
    end = opts._conf["EXIT"].split(",")
    entr = (int(start[1]), int(start[0]))
    exit = (int(end[1]), int(end[0]))
    base = "0123456789abcdef"
    sol = a_star(maze, entr, exit)
    with open(opts._conf['OUTPUT_FILE'], 'w') as out:
        for i in range(size[0]):
            for j in range(size[1]):
                out.write(base[maze[i][j]])
            out.write("\n")
        out.write("\n")
        out.write(f"{entr[1]},{entr[0]}\n")
        out.write(f"{exit[1]},{exit[0]}\n")
        out.write(sol)
    creation_draw(opts._conf['OUTPUT_FILE'], opts)
    time.sleep(1 / 16)


def maze_init(maze: NDArray[Any], visited: NDArray[Any]) -> tuple[int, int]:
    """Initialize the first tile of the maze"""
    h, w = maze.shape[:]
    v = -1
    while v == -1:
        current = (
            rng.randrange(0, h), rng.randrange(0, w)
        )
        v = visited[current[:]]
    visited[current[:]] = 1
    return current


def connect(
    maze: NDArray[Any], curr: tuple[int, int], neigh: tuple[int, int]
) -> None:
    """Connect two maze tiles"""
    if manhattan(curr, neigh) != 1:
        return
    if curr[0] == neigh[0] + 1 and get_walls(maze[curr[:]])[0] == 1:
        maze[curr[0]][curr[1]] -= 1
        maze[neigh[0]][neigh[1]] -= 4
    if curr[0] == neigh[0] - 1 and get_walls(maze[curr[:]])[2] == 1:
        maze[curr[0]][curr[1]] -= 4
        maze[neigh[0]][neigh[1]] -= 1
    if curr[1] == neigh[1] - 1 and get_walls(maze[curr[:]])[1] == 1:
        maze[curr[0]][curr[1]] -= 2
        maze[neigh[0]][neigh[1]] -= 8
    if curr[1] == neigh[1] + 1 and get_walls(maze[curr[:]])[3] == 1:
        maze[curr[0]][curr[1]] -= 8
        maze[neigh[0]][neigh[1]] -= 2


def direction() -> tuple[str, int]:
    """Choose a direction, return tuple"""
    if rng.random() < .5:
        axis = "V"
    else:
        axis = "H"
    if rng.random() < .5:
        step = -1
    else:
        step = 1
    return (axis, step)


def count_visited(visited: NDArray[Any]) -> int:
    """Return visited cells. Only if I merge Aldous-Broder and Wilson"""
    n = 0
    for i in range(visited.shape[0]):
        for j in range(visited.shape[1]):
            if visited[i][j] == 1:
                n += 1
    return n


def wilson_erase(
    visited: NDArray[Any], path: list[tuple[int, int]], point: tuple[int, int]
) -> None:
    """Erase a loop during random walk"""
    while path[-1] != point:
        visited[path[-1][:]] = 0
        path.pop()


def unvisited_set(visited: NDArray[Any]) -> set[tuple[int, int]]:
    """Make the unvisited tiles set"""
    yet = set()
    for i in range(visited.shape[0]):
        for j in range(visited.shape[1]):
            if visited[i, j] == 0:
                yet.add((i, j))
    return yet


def dfs(
        maze: NDArray[Any], visited: NDArray[Any], opts: _MazeOptions) -> None:
    current = maze_init(maze, visited)
    lst = [current]
    while len(lst) > 0:
        nvis = set()
        h, w = current[:]
        neighs = ((h - 1, w), (h, w + 1), (h + 1, w), (h, w - 1))
        for i in neighs:
            try:
                if True in [i[j] in (-1, maze.shape[j]) for j in [0, 1]]:
                    raise IndexError
                if visited[i[:]] == 0:
                    nvis.add(i[:])
            except IndexError:
                continue
        if len(nvis) == 0:
            lst.pop()
        else:
            new = rng.choice([*nvis])
            nvis.clear()
            connect(maze, current, new)
            visited[new[:]] = 1
            lst.append(new)
            write_path(maze, opts)
        try:
            current = lst[-1]
        except IndexError:
            pass


def prim(
        maze: NDArray[Any], visited: NDArray[Any], opts: _MazeOptions) -> None:
    current = maze_init(maze, visited)
    opened: set[tuple[int, int]] = set()
    opened.add(current)
    while len(opened) > 0:
        nvis = set()
        h, w = current[:]
        neighs = ((h - 1, w), (h, w + 1), (h + 1, w), (h, w - 1))
        for i in neighs:
            try:
                if True in [i[j] in (-1, maze.shape[j]) for j in [0, 1]]:
                    raise IndexError
                if visited[i[:]] == 0:
                    nvis.add(i[:])
            except IndexError:
                continue
        if len(nvis) == 0:
            opened.remove(current)
        else:
            new = rng.choice([*nvis])
            nvis.clear()
            connect(maze, current, new)
            visited[new[:]] = 1
            opened.add(new)
            write_path(maze, opts)
        if len(opened) > 0:
            current = rng.choice([*opened])


def aldous_broder(
        maze: NDArray[Any], visited: NDArray[Any], opts: _MazeOptions) -> None:
    current = maze_init(maze, visited)
    yet = unvisited_set(visited)
    while len(yet) > 0:
        direct = direction()
        try:
            if direct[0] == "V":
                neighbour = (current[0] + direct[1], current[1])
                if current[0] + direct[1] in (-1, maze.shape[0]):
                    raise IndexError
            else:
                neighbour = (current[0], current[1] + direct[1])
                if current[1] + direct[1] in (-1, maze.shape[1]):
                    raise IndexError
        except IndexError:
            continue
        if visited[neighbour[0], neighbour[1]] == -1:
            continue
        elif visited[neighbour[0], neighbour[1]] == 0:
            connect(maze, tuple[int, int](current), tuple[int, int](neighbour))
            write_path(maze, opts)
            yet.discard(neighbour)
        current = neighbour
        visited[current[0], current[1]] = 1


def wilson(
        maze: NDArray[Any], visited: NDArray[Any], opts: _MazeOptions) -> None:
    current = maze_init(maze, visited)
    yet = unvisited_set(visited)
    while len(yet) > 0:
        path = []
        current = rng.choice([*yet])
        visited[current[0], current[1]] = 2
        path.append(current)
        last_direction = ("x", 0)
        while current in yet:
            direct = direction()
            while last_direction == direct:
                direct = direction()
            try:
                if direct[0] == "V":
                    if current[0] + direct[1] in (-1, maze.shape[0]):
                        raise IndexError
                    neighbour = (current[0] + direct[1], current[1])
                else:
                    if current[1] + direct[1] in (-1, maze.shape[1]):
                        raise IndexError
                    neighbour = (current[0], current[1] + direct[1])
            except IndexError:
                continue
            if visited[neighbour[0], neighbour[1]] == -1:
                continue
            elif visited[neighbour[0], neighbour[1]] == 1:
                path.append(neighbour)
                break
            elif neighbour in path:
                wilson_erase(visited, path, neighbour)
            current = neighbour
            visited[current[0], current[1]] = 2
            if current not in path:
                path.append(current)
        for tile in path:
            visited[tile[0], tile[1]] = 1
            yet.discard(tile)
        while len(path) > 1:
            connect(maze, path[0], path[1])
            write_path(maze, opts)
            current = path[1]
            path.pop(0)
        path.clear()


def break_wall(maze: NDArray[Any], tile: tuple[int, int], op: str) -> None:
    """Connect the chosen tiles"""
    i, j = tile[:]
    if op == "N":
        connect(maze, tile, (i - 1, j))
    elif op == "E":
        connect(maze, tile, (i, j + 1))
    elif op == "S":
        connect(maze, tile, (i + 1, j))
    elif op == "W":
        connect(maze, tile, (i, j - 1))


def remove_walls(
    maze: NDArray[Any], tile: tuple[int, int], prob: float = 1
) -> None:
    """Check for neighbouring removable walls"""
    if maze[tile[:]] == 15 or prob < 0 or prob > 1:
        return
    i, j = tile[:]
    walls = get_walls(maze[tile[:]])
    r_walls = []
    if i > 0:
        if maze[i - 1][j] != 15 and walls[0] == 1:
            r_walls.append("N")
    if j < maze.shape[1] - 1:
        if maze[i][j + 1] != 15 and walls[1] == 1:
            r_walls.append("E")
    if i < maze.shape[0] - 1:
        if maze[i + 1][j] != 15 and walls[2] == 1:
            r_walls.append("S")
    if j > 0:
        if maze[i][j - 1] != 15 and walls[3] == 1:
            r_walls.append("W")
    if len(r_walls) > 0 and rng.random() < prob:
        break_wall(maze, tile, rng.choice(r_walls))


def imperfect(maze: NDArray[Any], opts: _MazeOptions) -> None:
    h, w = maze.shape
    """ Start connecting the four corners"""
    connect(maze, (0, 0), (0, 1))
    connect(maze, (0, 0), (1, 0))
    connect(maze, (0, w - 1), (0, w - 2))
    connect(maze, (0, w - 1), (1, w - 1))
    connect(maze, (h - 1, w - 1), (h - 1, w - 2))
    connect(maze, (h - 1, w - 1), (h - 2, w - 1))
    connect(maze, (h - 1, 0), (h - 1, 1))
    connect(maze, (h - 1, 0), (h - 2, 0))

    """Remove random walls in random tiles"""
    for _ in range(h * w // 3):
        tile = (rng.randrange(h), rng.randrange(w))
        remove_walls(maze, tile, .5)
        write_path(maze, opts)
    dead_ends = (7, 11, 13, 14)
    s_wall = ((0, 1), (0, 2), (0, 4), (0, 8))
    adm_walls = [1, 2, 3, 4, 5, 6, 8, 9, 10, 12]

    """Remove dead ends; ignores 42"""
    for i in range(h):
        for j in range(w):
            if maze[i, j] in dead_ends:
                remove_walls(maze, (i, j))
                write_path(maze, opts)

    """Check for areas > 3x3; fill them in such case"""
    for i in range(h):
        for j in range(w):
            if maze[i, j] == 0:
                adj_tiles = [(i - 1, j), (i, j + 1), (i + 1, j), (i, j - 1)]
                adj_walls = [
                    maze[
                        adj_tiles[k][:]
                    ] in s_wall[k] for k in range(len(adj_tiles))
                ]
                if False not in adj_walls:
                    maze[i, j] = rng.choice(adm_walls)
                    walls = get_walls(maze[i, j])
                    if walls[0] == 1:
                        maze[i - 1][j] += 4
                    if walls[1] == 1:
                        maze[i][j + 1] += 8
                    if walls[2] == 1:
                        maze[i + 1][j] += 1
                    if walls[3] == 1:
                        maze[i][j - 1] += 2
