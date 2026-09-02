# Maze Generator

## Description

This project contains a `MazeGenerator` class that can be used to generate mazes easily. The following structure will be needed to instantiate this class:

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

The variables `start` and `end`  need to have the structure `x[int],y[int]`. The range of the coordinates will be $0≤x,y<\text{height},\text{width}$. The class will not generate if:

* The entry and exit are the same tile.
* The entry or exit are out of bounds.
* The entry or exit are inside the previously mentioned `42`.

Upon instantiation, the class will automatically generate a maze ready for use.

The `MazeGenerator` class will have the following methods:

* `regen()`: Generates a new maze and solves it.
* `draw(solution: bool = False)`: Draws the maze in terminal. The `solution` variable decides whether to draw the maze solution or not.
* `color(key: str, color: list[int] = [])`: Changes the `key` color from the palette. The color must be a three-long list and all their values need to be 8-bit  unsigned integers. Any other value will remove the key from the palette, assigning a default color to it.
* `output(filename: str)`: Saves the maze, entry, exit and solution in a file named `filename`.

The `MazeGenerator` class also has the following properties:

* `maze`: A `Maze` private class containing the maze information. Printing this class will print its hexadecimal representation.
* `path`: A `Path` private class contaning information about the maze solution. Printing this class will print its NESW representation.
* `solution`: The maze solution from entry to exit as a NESW string.
* `palette`: A dictionary containing the colors of the maze upon drawing.

## Instructions

## Resources