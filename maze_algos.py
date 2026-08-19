from numpy.typing import NDArray
import random as rng
from maze_utils import manhattan


"""Initialize the first tile of the maze"""
def maze_init(maze: NDArray, visited: NDArray) -> tuple[int]:
    h, w = maze.shape[:]
    v = -1
    while v == -1:
        current = (
            rng.randrange(0, h - 1), rng.randrange(0, w - 1)
        )
        v = visited[current[:]]
    visited[current[:]] = 1
    return current


"""Connect two maze tiles"""
def connect(maze: NDArray, curr: tuple[int], neigh: tuple[int]) -> None:
    if manhattan(curr, neigh) != 1:
        return
        
    if curr[0] == neigh[0] + 1:
        maze[curr[0]][curr[1]] -= 1
        maze[neigh[0]][neigh[1]] -= 4
    if curr[0] == neigh[0] - 1:
        maze[curr[0]][curr[1]] -= 4
        maze[neigh[0]][neigh[1]] -= 1
    if curr[1] == neigh[1] - 1:
        maze[curr[0]][curr[1]] -= 2
        maze[neigh[0]][neigh[1]] -= 8
    if curr[1] == neigh[1] + 1:
        maze[curr[0]][curr[1]] -= 8
        maze[neigh[0]][neigh[1]] -= 2


"""Choose a direction, return tuple"""
def direction() -> tuple[str, int]:
    if rng.random() < .5:
        axis = "V"
    else:
        axis = "H"
    if rng.random() < .5:
        step = -1
    else:
        step = 1
    return (axis, step)


"""Return visited cells. Only if I decide to merge both algorithms"""
def count_visited(visited: NDArray) -> int:
    n = 0
    for i in range(visited.shape[0]):
        for j in range(visited.shape[1]):
            if visited[i][j] == 1:
                n += 1
    return n


"""Erase a loop during random walk"""
def wilson_erase(visited: NDArray, path: list[tuple], point: tuple[int]) -> None:
    while path[-1] != point:
        visited[path[-1][:]] = 0
        path.pop()


"""Make the unvisited tiles set"""
def unvisited_set(visited: NDArray) -> set:
    yet = set()
    for i in range(visited.shape[0]):
        for j in range(visited.shape[1]):
            if visited[i, j] == 0:
                yet.add((i, j))
    return yet


def dfs(maze: NDArray, visited: NDArray) -> None:
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
        try:
            current = lst[-1]
        except IndexError:
            pass


def prim(maze: NDArray, visited: NDArray) -> None:
    current = maze_init(maze, visited)
    yet = unvisited_set(visited)
    opened = set()
    opened.add(tuple(current))
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
        if len(opened) > 0:
            current = rng.choice([*opened])


def aldous_broder(maze: NDArray, visited: NDArray) -> None:
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
            connect(maze, tuple(current), tuple(neighbour))
            yet.discard(neighbour)
        current = neighbour
        visited[current[0], current[1]] = 1


def wilson(maze: NDArray, visited: NDArray) -> None:
    yet = unvisited_set(visited)
    while len(yet) > 0:
        path = []
        current = rng.choice([*yet])
        visited[current[0], current[1]] = 2
        path.append(current)
        last_direction = ()
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
            connect(maze, path[-2], path[-1])
            current = path[-1]
            path.pop()
        path.clear()
