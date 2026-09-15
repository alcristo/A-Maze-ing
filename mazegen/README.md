# mazegen: a maze generator package

## Description

This project contains a `MazeGenerator` class that can be used to generate mazes easily. The following structure will be needed to instantiate this class:

```python
class MazeGenerator

  def __init__(
        height: int,
        width: int,
        start: str,
        end: str,
        perfect: bool = False,
        seed: str | None = None,
        algorithm: str = "Prim"
  )
```

* `height` is the height of the maze.
* `width` is the width of the maze.
* `start` is the entry of the maze.
* `end` is the exit of the maze.
* `perfect` indicates whether there is only one path in the whole maze between two tiles. `False` will generate mazes with loops, perfect for chasing games.
* `seed` is the generation seed of the maze.
* `algorithm` is the maze generation algorithm. It supports the following algorithms:
  - `DFS`
  - `Prim`
  - `Wilson`
  - `Aldous-Broder`

The maze will generate a mandatory `42` with height 5 and width 7 at the center of the maze, made of tiles with walls on all four sides, if the maze size has over 6 rows and 8 columns, both numbers not included.

The variables `start` and `end`  need to have the structure "$x,y$", being both $x$ and $y$ integers. The range of the coordinates will be $0≤x,y<\text{height},\text{width}$. The class will not generate if:

* The entry and exit are the same tile.
* The entry or exit are out of bounds.
* The entry or exit are inside the previously mentioned `42`.

Upon instantiation, the class will automatically generate a maze ready for use.

The `MazeGenerator` class will have the following methods:

* `regen()`: Generates a new maze and solves it. It will not do nothing if the maze is not valid.
* `draw(solution: bool = False)`: Draws the maze in terminal. The `solution` variable decides whether to draw the maze solution or not.
* `color(key: str, color: list[int] = [])`: Changes the `key` color from the palette. The color must be a three-long list and all their values need to be 8-bit  unsigned integers. Any other value will remove the key from the palette, assigning a default color to it.
* `output(filename: str)`: Saves the maze, entry, exit and solution in a file named `filename`, extension included.

The `MazeGenerator` class also has the following properties:

* `maze`: A `Maze` private class containing the maze information. Printing this class will print its hexadecimal representation.
* `path`: A `Path` private class contaning information about the maze solution. Printing this class will print its NESW representation.
* `solution`: The maze solution from entry to exit as a NESW string.
* `palette`: A dictionary containing the colors of the maze upon drawing.

### Algorithms

For the maze generation, the maze is at first made entirely with fully closed tiles. An auxiliary array will keep track of visited tiles, while storing the `42` structure. All maze generation algorithms start with a random tile set as visited, and therefore part of the maze. Four maze generation algorithms were implemented:

* Wilson's algorithm: This algorithm generates an uniform spanning tree; in other words, with this algorithm all possible mazes are equally probable. Wilson's algorithm is based on a loop-erase random walk:
  1. A non-visited tile is chosen and made it the starting point for performing a random walk.
  2. When the path visits a tile within itself, the loop until that point gets erased, in which continues the random walk.
  3. If the path gets into the maze it becomes part of it. Repeat step 1.

  Wilson's algorithm has the downside of being slow at the beginning, especially in really large mazes, but the generation accelerates once the first path becomes part of the maze.

* Aldous-Broder algorithm: Like Wilson's, this algorithm also generates an uniform spanning tree.
  1. A point performs a random walk through all the maze boundaries, starting from the initial tile.
  2. If such point walks into a non-visited tile, it gets connected to the previous tile, which will always be part of the maze.
  3. If the point walks into an already visited tile, it does nothing. The point can ignore maze walls while moving, but not the maze boundaries.
  
  Like Wilson's, Aldous-Broder algorithm is also slower than other algorithms in huge mazes, especially at the end, when there are few stray tiles in the maze that may take time to connect. Usually both Wilson and Aldous-Broder algorithms are combined together, starting with the latter until a third part of the area and then switching to the former.

* Prim's algorithm: A simple maze generation algorithm which is faster than the previous ones. 
  1. Starting with a random tile as the maze, which becomes part of a set, one of their unvisited neighbouring tiles get into that set.
  2. One of the tiles in the set is selected randomly to repeat step 1.
  3. When one of the tiles has no neighbours to visit, it is taken out of the set. The generation stops when the set is empty.

  Prim's algorithm has the downside of generating mazes with many short dead-ends. In bigger mazes, a bias towards the initial point of generation can be seen.

* Depth First Search: Another simple maze generation algorithm.
  1. A random path from the starting tile to unvisited tiles is performed.
  2. When the path can't continue due to the current tile not having neighbours to visit, it backtracks until a tile with unvisited neighbours is reached, and step 1 repeats itself. This is why this method is also known as the *recursive backtracker*.
  
  This algorithm is fast, although the mazes are biased towards very long paths. When visualizing the solution, this fact is clearer due to its length compared to the ones in other algorithms. There is a variation of this algorithm called *hunt & kill*, where, instead of backtracking, the maze is scanned until a tile with neighbours to visit is found.

If the `perfect` keyword argument is set to `False`, then a maze braiding algorithm is triggered after the perfect generation, no matter which algorithm was used to generate the maze:

1. The corners are set to hardcoded values and their neighbours are connected coherently.
2. Random tiles are selected and one of their walls is removed.
3. The whole maze is scanned to search dead-end tiles and remove one of their walls.
4. The maze is scanned again, this time to find open areas (with 3x3 as the minimum of dimensions) and random walls (no dead ends) are added at the center.

This way the maze will be perfectly braided, except for the `42` structure. This algorithm will not run if the maze has height or width equal to one.

The A* algorithm was implemented to solve the maze. A* is one of the best pathfinding algorithms if using the right heuristic (way to decide): it's used in areas from videogames to maps. It uses three variables: *G score*, which is the distance from the starting node to the current node, *H score*, which is the same but from current node to finish node, and the *F score*, the sum of *G* and *H* scores. At the start of the A* algorithm, two sets defined as *open* and *closed* are defined. The open set contains the entry node and the closed set is empty. So, the A* algorithm runs as follows:

1. A node from such open set is moved to a closed set.
2. *G*, *H* and *F* scores are calculated for each tile neighbouring the current one, regarding they do not belong to the closed set.
3. If *F* score lower than the one calculated in a previous step, update the node in the open set.
4. If that tile is not in the open or closed sets, add the node containing it to the open set.
5. Select the node with the lowest *F* score.
  - If there is a tie in *F* score, select the node with the lowest *H* score.
  - If a tie persists, choose one of those nodes randomly.
6. Repeat step 1 with the selected node.

The performance of the A* algorithm depends on the heuristics defined to search the exit. In our case, we selected the Manhattan heuristic:

$$
H = \left|x_{tile} - x_{exit}\right| + \left|y_{tile} - y_{exit}\right|
$$

The Manhattan heuristics is perfect for maze solving because of the movement restrictions: you can only move north, east, south and west, but not a linear combination of north-south and east-west axes. If such were the case, then the Euclidean heuristic would perform better:

$$
H = \sqrt{\left(x_{tile} - x_{exit}\right)^2 + \left(y_{tile} - y_{exit}\right)^2}
$$

It's not unusual the use of Euclidean heuristics to solve these mazes, but it would take longer. Nonetheless, such heuristic will find the shortest path too. If no heuristics are used, the A* algorithm becomes *Dijkstra's algorithm*.

## Instructions

To install the package, copy the wheel file `mazegen-[VERSION]-py3-none-any.whl` to a project and then run in a virtual environment:

```bash
pip install mazegen
```

To use the `MazeGenerator` class in a script, import it to the script:

```python
from mazegen import MazeGenerator
```

## Resources

[My A-Maze-ing project](https://github.com/alcristo/A-Maze-ing), with all its subsequent resources.