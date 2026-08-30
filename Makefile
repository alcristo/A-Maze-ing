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
	pdb $(NAME) $(CONFIG)

clean:
	$(RM) $(CACHE)

lint:
	flake8 && mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs && make clean

lint-strict:
	flake8 && mypy . --strict&& make clean
