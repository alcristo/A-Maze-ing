NAME = a_maze_ing.py

CONFIG = config.txt

PYTHON = python3

REQUIREMENTS = numpy

CACHE = __pycache__ \
		.mypy_cache

RM = rm -rf


install:
	pip install $(REQUIREMENTS)

run:
	$(PYTHON) $(NAME) $(CONFIG) && make clean

debug:
	$(PYTHON) -m pdb $(NAME) $(CONFIG)

clean:
	$(RM) $(CACHE)

lint:
	$(PYTHON) -m flake8 && $(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs && make clean

lint-strict:
	$(PYTHON) -m flake8 && $(PYTHON) -m mypy . --strict && make clean
