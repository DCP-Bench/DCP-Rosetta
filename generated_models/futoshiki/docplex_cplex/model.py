# futoshiki: a CPLEX (Python) model from DCP Rosetta.
# Download the `futoshiki.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python futoshiki.py futoshiki.json

from docplex.mp.model import Model


def create_model(instance):
    """Futoshiki: fill an n-by-n grid with 1..n so that every row and every column holds different
    numbers, the given numbers stay, and every "less than" sign between two cells holds."""
    values = instance["values"]  # values[i][j]: the given number in row i, column j; 0 if not set
    lt = instance["lt"]          # [i1, j1, i2, j2], 1-based: cell (i1, j1) < cell (i2, j2)
    size = len(values)
    cells = range(size)
    numbers = range(1, size + 1)

    model = Model("futoshiki")

    # has[i, j, v] is 1 when cell (i, j) holds v; every cell holds one number.
    has = {(i, j, v): model.binary_var(name=f"has_{i}_{j}_{v}") for i in cells for j in cells for v in numbers}
    model.add_constraints(model.sum(has[i, j, v] for v in numbers) == 1 for i in cells for j in cells)
    grid = [[model.sum(v * has[i, j, v] for v in numbers) for j in cells] for i in cells]

    # The numbers given at the start stay.
    model.add_constraints(grid[i][j] == values[i][j] for i in cells for j in cells if values[i][j] > 0)

    # Each row and each column holds every number exactly once.
    model.add_constraints(model.sum(has[i, j, v] for j in cells) == 1 for v in numbers for i in cells)
    model.add_constraints(model.sum(has[i, j, v] for i in cells) == 1 for v in numbers for j in cells)

    # Every "less than" sign holds: the first cell is lower than the second (the positions are
    # 1-based; for whole numbers, lower means at least one less).
    model.add_constraints(grid[i1 - 1][j1 - 1] + 1 <= grid[i2 - 1][j2 - 1] for i1, j1, i2, j2 in lt)

    return model, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
