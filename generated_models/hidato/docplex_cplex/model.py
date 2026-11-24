# hidato: a CPLEX (Python) model from DCP Rosetta.
# Download the `hidato.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python hidato.py hidato.json

from docplex.mp.model import Model


def create_model(instance):
    """Hidato: fill the empty cells of an r-by-c grid with the numbers 1..r*c, each used once and
    the given numbers kept, so that every number k < r*c has k + 1 in one of its eight
    neighbouring cells (a king's move away)."""
    puzzle = instance["puzzle"]  # 0 marks an empty cell; other cells hold their given number
    r, c = len(puzzle), len(puzzle[0])  # the number of rows and of columns
    total = r * c

    # given[k] is the cell where the number k is already placed; empty lists the cells to fill
    # and missing the numbers still to place.
    given = {puzzle[i][j]: (i, j) for i in range(r) for j in range(c) if puzzle[i][j] > 0}
    empty = [(i, j) for i in range(r) for j in range(c) if puzzle[i][j] == 0]
    missing = [k for k in range(1, total + 1) if k not in given]

    def distance(p, q):
        # Number of king's moves between two cells.
        return max(abs(p[0] - q[0]), abs(p[1] - q[1]))

    model = Model("hidato")

    # An empty cell q can hold the missing number k only if every given number g is at least
    # as many steps away along the path as q is king's moves from g's cell: |k - g| >=
    # distance. Numbers that fail this cannot go there in any solution, so they get no
    # variable; this keeps the 12-by-12 grid (144 numbers per cell) inside the Community
    # Edition's 1000 variables.
    candidates = {q: [k for k in missing if all(abs(k - g) >= distance(q, p) for g, p in given.items())]
                  for q in empty}

    # holds[q, k] is 1 when empty cell q holds the number k.
    holds = {(q, k): model.binary_var(name=f"holds_{q[0]}_{q[1]}_{k}") for q in empty for k in candidates[q]}

    # Every empty cell holds one number, and every missing number is placed in one cell: with
    # the given numbers, the numbers 1..r*c are all different.
    model.add_constraints(model.sum(holds[q, k] for k in candidates[q]) == 1 for q in empty)
    model.add_constraints(model.sum(holds[q, k] for q in empty if (q, k) in holds) == 1 for k in missing)

    def neighbours(q):
        return [(q[0] + a, q[1] + b) for a in (-1, 0, 1) for b in (-1, 0, 1)
                if (a, b) != (0, 0) and 0 <= q[0] + a < r and 0 <= q[1] + b < c]

    def number_at(q, k):
        # 1 when cell q holds k: a constant for a given cell, a variable (or 0) for an empty one.
        if puzzle[q[0]][q[1]] > 0:
            return 1 if puzzle[q[0]][q[1]] == k else 0
        return holds[q, k] if (q, k) in holds else 0

    # Each number k below r*c has k + 1 in a neighbouring cell. For a given k this is one
    # constraint on its neighbours; for a missing k, one per cell that may hold it.
    for k in range(1, total):
        if k in given:
            p = given[k]
            model.add_constraint(model.sum(number_at(q, k + 1) for q in neighbours(p)) >= 1)
        else:
            for q in empty:
                if (q, k) in holds:
                    model.add_constraint(holds[q, k] <= model.sum(number_at(n, k + 1) for n in neighbours(q)))

    # x[i][j] is the number in cell (i, j).
    x = [[puzzle[i][j] if puzzle[i][j] > 0 else model.sum(k * holds[(i, j), k] for k in candidates[(i, j)])
          for j in range(c)] for i in range(r)]

    return model, {"x": x}


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
