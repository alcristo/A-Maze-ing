NAME = a_maze_ing.py

CONFIG = config.txt

PYTHON = python3

PIP = pip install

REQUIREMENTS = -r requirements.txt

SOURCES =	a_maze_ing.py \
			maze_algos.py \
			maze_utils.py \
			pathfinding.py \
			maze_draw.py \
			gameplay.py \
			maze_generator.py

CACHE = __pycache__ \
		.mypy_cache

RM = rm -rf

LINT = flake8 $(SOURCES) && mypy $(SOURCES)


install:
	$(PIP) $(REQUIREMENTS)

run: clean
	$(PYTHON) $(NAME) $(CONFIG) && make clean

debug:
	$(PYTHON) -m pdb $(NAME) $(CONFIG)

clean:
	$(RM) $(CACHE)

lint: clean
	$(LINT) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs && make clean

lint-strict: clean
	$(LINT) --strict && make clean
