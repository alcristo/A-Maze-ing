*This project was made as part of the 42 curriculum by alcristo and*

# A-Maze-ing

## Description

This project consists in the generation, resolution and visualization of mazes using Python. External package `numpy` was used for maze storage in matrices. A configuration file would be needed in order to generate the maze. The program will:

* Generate the maze.
* Solve the maze.
* Save the maze in an output file.
* Draw the maze in terminal.
* Go to a menu with several options.

### The configuration file

The configuration file is a readable text file with the following structure:

    VARIABLE=value\n

The configuration file will ignore every other line that does not comply this structure, let it be a single variable, an empty line or a line with more than two `=` characters. The variable name does not have to be necessarily uppercase. A hash character (#) as the first character of a variable indicates that this variable is a comment and, therefore, should be ommited.

There are several options in the configuration file:

* HEIGHT: Mandatory. The height of the maze in tiles. Must be an integer.
* WIDTH: Mandatory. The width of the maze in tiles. Must be an integer.
* ENTRY: Mandatory. The entry tile of the maze. Format: `x,y`, being $0 \leq x < WIDTH$ and $0 \leq y < HEIGHT$.
* EXIT: Mandatory. The exit tile of the maze. Same format as entry; must not be equal to exit.
* OUTPUT_FILE: Mandatory. The file where the maze will be printed in order to be drawn.
* PERFECT: Whether the maze is perfect (there is only one path between two separate points) or not perfect (there can be loops in the path). Defaults to `True`.
* SEED: The seed to generate the maze. Defaults to `None`.
* ALGORITHM: The maze generation algorithm. Accepts `aldous broder`, `recursive backtracker`, `depth first search`, `prim` and `wilson`. All options accept no space, snake case space (also - space for Aldous-Broder) and acronyms, as well as any ASCII case format. Defaults to `Prim`.

### Maze format

The maze will be stored in a `numpy` array, so tiles are accessed as `array[y, x]`. For this reason, the entry and exit tiles will have their coordinates inverted for computing simplicity, but will be back in order for user access files.

The maze tiles are stored in numbers from 0 to 15 in order to later format the maze as hexadecimal numbers. These hexadecimal numbers have four bits, each one representing which walls are open (0) or closed (1). From least to most significant bit, the represented walls are North, East, South and West. Tiles in the maze are coherent with their neighbours, meaning that if the northern wall of a tile is closed, the southern wall of its northern neighbour is also closed. This coherence extends to the box borders.

If the maze height is above 6 and the maze width is above 8, a mandatory `42` made of fully closed tiles (value 15, f) will be generated at the center of the maze. If this condition is not satisfied, an error message will be displayed, but the maze will still be generated. Neither the maze entry nor the exit can be generated inside the `42`.

### Maze generation algorithms

At first, the maze is made in its totality with fully closed tiles. An auxiliary array will keep track of visited tiles, while storing the `42` structure. All maze generation algorithms start with a random tile set as visited, and therefore part of the maze.

One generation algorithm was said to be implemented in this project, but more than one was graded as a bonus. We implemented four algorithms in total:

* Wilson's algorithm: This was the first algorithm implemented in the project. We chose it because it generates an infinite spanning tree; in other words, with this algorithm all mazes are equally probable. Wilson's algorithm is based on a loop-erase random walk: starting from a random point as the maze, we choose a non-visited tile and make it perform a random walk. When the path hits itself, it gets erased until that point, in which continues the random walk. If the path gets into the maze it becomes part of it, and another non-visited tile is selected to perform another random walk. However, Wilson's algorithm has the downside of being slow at the beginning, especially in really large mazes, but the generation accelerates once the first path becomes part of the maze.
* Aldous-Broder algorithm: Like Wilson's, this algorithm also generates an infinite spanning tree. Starting from a point considered part of the maze, a point performs a random walk through all the box. If such point walks into a non-visited tile, it gets connected to the previous tile, which will always be part of the maze. Like Wilson's, Aldous-Broder algorithm is also slower than other algorithms in huge mazes, especially at the end, when there are few stray tiles in the maze that may take time to connect. Usually both Wilson and Aldous-Broder algorithms are combined together, starting with the latter until a third part of the area and then switching to the former.
* Prim's algorithm: starting with a random tile as the maze, which becomes part of a set, one of their unvisited neighbouring tiles get into that set. Then, one of the tiles in the set is selected randomly to repeat this process. When one of the tiles has no neighbours to visit, it is taken out of the set. The generation stops when the set is empty. Prim's algorithm is faster than the previous algorithms, but the generated mazes are usually biased towards the initial point of generation.
* Depth First Search: starting from a random tile, a random path is made. When the path can't continue due to the current tile not having neighbours to visit, it backtracks until a tile with unvisited neighbours is reached, and this process continues. This is why this method is also known as the *recursive backtracker*. This algorithm is fast, although the mazes are biased towards very long paths, which can be seen in the solution. There is a variation of this algorithm called *hunt & kill*, where, instead of backtracking, the maze is scanned until a tile where the algorithm can continue is found.

If the option *PERFECT* is set to *False*, then another algorithm is triggerd after the perfect generation. First, the corners are set to hardcoded values and the neighbours are connected coherently. Then, random tiles are selected and one of their walls is removed. Next, the whole maze is scanned to search dead-end tiles and remove one of their walls. Finally, the maze is scanned again, this time to find open areas (with 3x3 as the minimum of dimensions) and random walls are added at the center.

### Pathfinding algorithm

To solve the maze, the usual strategy is to grab a wall and follow it until the exit is reached. However, in looped mazes this strategy can actually cause one to loop around a wall. So, the next coherent strategy would be flood-filled based: you start at the entry and start flooding the neighbouring areas until the exit is eventually reached. Despite its ability to find the shortest path, these algorithms search even areas that one would ignore because, for example, they are actively going away from the exit. So, a *heuristic* (a way to decide) is needed to choose which path to follow next.

A* algorithm is one of the best pathfinding algorithms fi using the right heuristic: it's used in areas from videogames to maps. It uses three variables: *G score*, which is the distance from the starting node to the current node, *H score*, which is the same but from current node to finish node, and the *F score*, the sum of *G* and *H* scores.

First, the entry node is saved to an open set. Then, a node from such open set is moved to a closed set, and all their neighbours are added to the open set, calculating the *F* scores and heuristics of each one, and updating them in case *F* or *G* scores are actually lower. Finally, the node with the lowest *F* score is selected and the process is repeated until the exit is reached. If two tiles have the same *F* score, the one with the lowest *H* score is selected, for it would be the nearest to the exit. If a tie between tiles exists, then one of them is selected randomly.

The performance of the A* algorithm depends on the heuristics defined to search the exit. In our case, we selected the Manhattan heuristic:

$$
H = \left|x_{tile} - x_{exit}\right| + \left|y_{tile} - y_{exit}\right|
$$

The Manhattan heuristics is perfect for maze solving because of the movement restrictions: you can only move north, east, south and west, but not a linear combination of north-south and east-west axes. If such were the case, then the Euclidean heuristic would perform better:

$$
H = \sqrt{\left(x_{tile} - x_{exit}\right)^2 + \left(y_{tile} - y_{exit}\right)^2}
$$

It's not unusual the use of Euclidean heuristics to solve these mazes, but it would take longer. Nonetheless, such heuristic will find the shortest path too.

### Visual representation

In order to draw the maze in terminal, spaces would represent both the whole maze grid, while ANSI escape sequences were coded to change the colors to distinguish tiles from walls. The default color palette is, in ANSI escape code:

    tiles: \x1b[47m
    walls: \x1b[40m
    entry: \x1b[45m
    exit:  \x1b[42m
    path:  \x1b[44m
    block: \x1b[41m

Nonetheless, the color palette can be changed in the menu (see instructions). This menu has also an option to hide the solution.

### Reusable code

The file in the folder `./MazeGenerator` contains a `MazeGenerator` class that may be needed in future projects. This class has the following methods:

## Instructions

## Resources

### AI Usage

Artificial intelligence was used to debug and correct code, as well as giving ideas about the maze representation.