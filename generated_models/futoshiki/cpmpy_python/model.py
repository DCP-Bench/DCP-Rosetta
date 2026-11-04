# futoshiki: a CPMpy model from DCP Rosetta.
# Download the `futoshiki.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python futoshiki.py futoshiki.json

import cpmpy as cp


def create_model(instance):
    """Futoshiki: fill an n-by-n grid with the numbers 1 to n so that every row and
    column holds each number once, the given numbers are in place, and the
    inequality signs between neighbouring cells hold."""
    values = instance["values"]  # values[i][j]: the given number in row i, column j; 0 means empty
    lt = instance["lt"]          # each [i1, j1, i2, j2] (1-based) requires cell (i1, j1) < cell (i2, j2)
    size = len(values)

    # grid[i, j] is the number in row i, column j
    grid = cp.intvar(1, size, shape=(size, size), name="grid")

    model = cp.Model()

    # The numbers given at the start are fixed.
    for i in range(size):
        for j in range(size):
            if values[i][j] > 0:
                model.add(grid[i, j] == values[i][j])

    # Every row contains each number once.
    for i in range(size):
        model.add(cp.AllDifferent(grid[i, :]))

    # Every column contains each number once.
    for j in range(size):
        model.add(cp.AllDifferent(grid[:, j]))

    # Every inequality sign holds: the first cell is smaller than the second (cells are 1-based in the data).
    for i1, j1, i2, j2 in lt:
        model.add(grid[i1 - 1, j1 - 1] < grid[i2 - 1, j2 - 1])

    return model, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
