*This project was made as part of the 42 curriculum by [alcristo](https://github.com/alcristo) and [pnarvaez](https://github.com/Pau-Narvaez-Roy).*

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
* ENTRY: Mandatory. The entry tile of the maze. Format: `x,y`, being $0 \leq x < \text{WIDTH}$ and $0 \leq y < \text{HEIGHT}$.
* EXIT: Mandatory. The exit tile of the maze. Same format as entry, but both entry and exit must not be equal.
* OUTPUT_FILE: Mandatory. The file where the maze will be printed in order to be drawn.
* PERFECT: Whether the maze is perfect (there is only one path between two separate points) or not perfect (there can be loops in the path). Defaults to `True`.
* SEED: The seed to generate the maze. Defaults to `None`.
* ALGORITHM: The maze generation algorithm. Accepts `aldous broder`, `recursive backtracker`, `depth first search`, `prim` and `wilson`. All options accept no space, snake case space (also - space for Aldous-Broder) and acronyms, as well as any ASCII case format. Defaults to `Prim`.
* ANIMATE: Whether to show the maze generation. Defaults to `False`. The animation will not trigger if  the maze has more than 700 tiles (for a square maze, the maximum length to trigger the animation will be 26).

### Maze format

The maze will be stored in a `numpy` array, so tiles are accessed as `array[y, x]`. For this reason, the entry and exit tiles will have their coordinates swapped for computing simplicity, but will be back in order for user access files.

The maze tiles are stored in numbers from 0 to 15 in order to later format the maze as hexadecimal numbers. These hexadecimal numbers have four bits, each one representing which walls are open (0) or closed (1). From least to most significant bit, the represented walls are North, East, South and West. Tiles in the maze are coherent with their neighbours, meaning that if the northern wall of a tile is closed, the southern wall of its northern neighbour is also closed. This coherence extends to the box borders.

If the maze height is above 6 and the maze width is above 8, a mandatory `42` made of fully closed tiles (value 15, f) will be generated at the center of the maze. If this condition is not satisfied, an error message will be displayed, but the maze will still be generated. Neither the maze entry nor the exit can be generated inside the `42`.

Finally, the maze will not be generated if the total area exceeds 26000 tiles. For example, the maximum square maze that will generate is 161 tiles long.

### Maze generation algorithms

One generation algorithm was said to be implemented in this project, but more than one was graded as a bonus.

At first, the maze is made entirely with fully closed tiles. An auxiliary array will keep track of visited tiles, while storing the `42` structure. Every maze generation algorithm implemented in this project starts with a random tile marked as visited, which becomes part of the maze. We implemented four algorithms in total:

* Wilson's algorithm: This was the first algorithm implemented in the project. We chose it because it generates an uniform spanning tree; in other words, with this algorithm all possible mazes are equally probable. Wilson's algorithm is based on a loop-erase random walk:
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

If the option *PERFECT* is set to *False*, then another algorithm is triggered after the perfect generation, no matter which algorithm was used to generate the maze:

1. The corners are set to hardcoded values and their neighbours are connected coherently.
2. Random tiles are selected and one of their walls is removed.
3. The whole maze is scanned to search dead-end tiles and remove one of their walls.
4. The maze is scanned again, this time to find open areas (with 3x3 as the minimum of dimensions) and random walls (no dead ends) are added at the center.

This way the maze will be perfectly braided, except for the `42` structure. This algorithm will not run if the maze has height or width equal to one.

### Pathfinding algorithm

To solve the maze, the usual strategy is to grab a wall and follow it until the exit is reached. However, in looped mazes this strategy can actually cause one to loop around a wall. So, the next coherent strategy would be flood-filled based: you start at the entry and start flooding the neighbouring areas until the exit is eventually reached. Despite its ability to find the shortest path, these algorithms search even areas that one would ignore because, for example, they are actively going away from the exit. So, a *heuristic* (a way to decide) is needed to choose which path to follow next.

A* algorithm is one of the best pathfinding algorithms if using the right heuristic: it's used in areas from videogames to maps. It uses three variables: *G score*, which is the distance from the starting node to the current node, *H score*, which is the same but from current node to finish node, and the *F score*, the sum of *G* and *H* scores. At the start of the A* algorithm, two sets defined as *open* and *closed* are defined. The open set contains the entry node and the closed set is empty. So, the A* algorithm runs as follows:

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

It's not unusual the use of Euclidean heuristics to solve these mazes, but it would take longer. Nonetheless, such heuristic will find the shortest path too. If no heuristics are used, the A* algorithm becomes *Djikstra's algorithm*.

### Visual representation

In order to draw the maze in terminal, spaces would represent both the whole maze grid, while ANSI escape sequences were coded to change the colors to distinguish tiles from walls. The default color palette is, in ANSI escape code:

    tiles:  \x1b[47m
    walls:  \x1b[40m
    entry:  \x1b[45m
    exit:   \x1b[42m
    path:   \x1b[44m
    block:  \x1b[41m
    player: \x1b[46m

Nonetheless, the color palette can be changed in the menu (see [instructions](#color-selection-menu)). This menu has also an option to hide the solution.

### Reusable code

The file in the folder `./MazeGenerator` contains a `MazeGenerator` class that may be needed in future projects. The following structure will be needed to instantiate this class:

```python
MazeGenerator(
        height: int,
        width: int,
        start: str,
        end: str,
        perfect: bool = False,
        seed: str | None = None,
        algorithm: str = "Prim"
)
```

The variables `start` and `end` will be the entry annd exit of the maze respectively, and need to have the structure `"{int},{int}"`, just like in the configuration file from the main program, except for the quotes.

Upon instantiation, the class will automatically generate a maze ready for use.

The `MazeGenerator` class will have the following methods:

* `regen()`: Generates a new maze and solves it. It will not do nothing if the maze is not valid.
* `draw(solution: bool = False)`: Draws the maze in terminal. The `solution` variable decides whether to draw the maze solution or not.
* `color(key: str, color: list[int] = [])`: Changes the `key` color from the palette. The color must be a three-long list and all their values need to be 8-bit  unsigned integers. Any other value will remove the key from the palette, assigning a default color to it.
* `output(filename: str)`: Saves the maze, entry, exit and solution in a file named `filename`.

The `MazeGenerator` class also has the following properties:

* `maze`: A `Maze` private class containing the maze information. Printing this class will print its hexadecimal representation.
* `path`: A `Path` private class contaning information about the maze solution. Printing this class will print its NESW representation.
* `solution`: The maze solution from entry to exit as a NESW string.
* `palette`: A dictionary containing the colors of the maze upon drawing.


### Team and project management

* `alcristo` handled the code structuration, algorithm development, and the maze creation, solution, graphics, and configuration while `pnarvaez` handled the maze animation, gameplay mode, and player-related gameplay.
* Originally, `pnarvaez` would have managed the graphics, but due to some problems `alcristo` had to handle it. Nonetheless, `pnarvaez` did an excellent job with their part of the project.
* The code in his idea works well, we could have added more playable possibilities like a 3D maze, even more algorithm support like Eller's or Krunskal's or cleaned some reused code. 

## Instructions

In order to run this project, you need to have a valid configuration file named `config.txt`. Otherwise, a custom configuration menu will appear. Following correctly the instructions of this menu will run the rest of the maze generation.

A Makefile will be attached to this project. It has the following rules:

* install: installs all necessary packages using `pip`.
* run: runs the program. Cleans all temporary files and caches before and after running.
* debug: runs the program with `pdb`.
* clean: removes temporary files and caches.
* lint: executes `flake8` and `mypy` to make sure the code is well structured and type-hinted.
* lint-strict: executes `flake8` and `mypy --strict` for a strict hint typing.

To execute one of these rules, run in terminal:

```bash
make <rule>
```

After the maze has been drawn a menu will appear. Such menu has the following configurations:

    1. Generate a new maze with the current configuration
    2. Show or hide the shortest solution
    3. Change the color palette
    4. Change the configuration
    5. Play
    q. Quit the program

### Color selection menu

A new menu will appear if option number 3 is chosen. This menu will have this style at first time:

    1. Tile
    2. Wall
    3. Entry
    4. Exit
    5. Path
    6. Block
    7. Player
    d. Change all colors to default palette
    q. Quit color selection menu

All options will have their current color (the default palette for the first time, see [Visual representation](#visual-representation)). To change a color, select it and you will need to input three unsigned 8-bit integers (also known as `uint8` \[0-255\]), each one for each color channel (RGB). Invalid inputs will leave the color unchanged. The colors are updated in the maze.

### Configuration changing menu

Another menu will appear after choosing 'Change the configuration' option:

    1. Height
    2. Width
    3. Entry
    4. Exit
    5. Output file
    6. Perfect
    7. Seed
    8. Algorithm
    9. Animation
    d. Default braided maze
    u. Undo all changes
    q. Quit configuration selector menu

Like the color selection menu, this one will show their current setting. This menu is foolproof: if you try to make a faulty maze (for example, with negative dimensions or entry/exit out of bounds) you would not be able to quit the menu. After exiting this menu with different settings, generating a new maze will draw a maze with the selected settings.

The default braided can be generated at start if the `config.txt` file has this structure:

```text
HEIGHT=15
WIDTH=31
ENTRY=0,7
EXIT=30,7
PERFECT=False
OUTPUT_FILE=default_maze.txt
SEED=alcristo
ALGORITHM=Wilson
ANIMATE=True
```

### Gameplay 

The maze has a built-in game mode, so the maze can be playable. To move the player, just press the following keys:

1. w or up arrow to go north
2. s or down arrow to go south
3. a or left arrow to go west
4. d or right arrow to go east
5. q to exit the game mode

The game will end when the player gets to the exit or when the user presses `q`. The player will return to the maze entry afterwards.

### Maze Generator

To install the `MazeGenerator` class, run in terminal:

```bash
python -m build
```

This will generate a `/dist` directory with two files:

* A `mazegen-[...].tar.gz`.
* A `mazegen-[...].whl`.

To install either of them, copy either of the files to a project and then run:

```bash
pip install mazegen
```

To use the `MazeGenerator` class, run in Python:

```python
from mazegen.mazegen import MazeGenerator
```

## Resources

Wikipedia pages for [Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm) and [A* search algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm) were used as reference for docmuentation.

ConnerWill's [ANSI escape sequences cheatsheet](https://gist.github.com/ConnerWill/d4b6c776b509add763e17f9f113fd25b) helped with the maze drawing.

Python's official documentation for [pyproject.toml writing](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) was used to write the `pyproject.toml`.

### AI Usage

Artificial intelligence was used to debug and correct code, as well as giving ideas about the maze representation.