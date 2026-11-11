# csplib_067_quasigroup_completion: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_067_quasigroup_completion.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_067_quasigroup_completion.py csplib_067_quasigroup_completion.json

from docplex.mp.model import Model


def create_model(instance):
    """Quasigroup completion: fill the empty cells of a partly filled N-by-N grid with 1..N so that
    it becomes a Latin square, every row and every column holding each number once."""
    N = instance["N"]          # size of the quasigroup (Latin square)
    start = instance["start"]  # initial board; 0 marks an empty cell

    cells = range(N)         # the row and column indices
    values = range(1, N + 1)  # the numbers a cell can hold

    model = Model("quasigroup_completion")

    # The cells can hold the numbers 1..N. A filled cell keeps its starting number. An empty
    # cell cannot take a number already given in its row or column, so those values get no
    # variable; this keeps N = 10 inside the Community Edition's 1000 variables.
    def allowed(i, j):
        if start[i][j] != 0:
            return [start[i][j]] if 1 <= start[i][j] <= N else []
        given = {start[i][k] for k in cells} | {start[k][j] for k in cells}
        return [v for v in values if v not in given]

    # has[i, j, v] is 1 when cell (i, j) holds v; every cell holds exactly one number, and a
    # filled cell holds its starting number.
    has = {}
    for i in cells:
        for j in cells:
            options = allowed(i, j)
            for v in options:
                has[i, j, v] = model.binary_var(name=f"has_{i}_{j}_{v}")
            model.add_constraint(model.sum(has[i, j, v] for v in options) == 1)

    # puzzle[i][j] is the number in cell (i, j).
    puzzle = [[model.sum(v * has[i, j, v] for v in values if (i, j, v) in has) for j in cells] for i in cells]

    # Each row and each column contains each number from 1 to N once.
    for v in values:
        for i in cells:
            model.add_constraint(model.sum(has[i, j, v] for j in cells if (i, j, v) in has) == 1)
        for j in cells:
            model.add_constraint(model.sum(has[i, j, v] for i in cells if (i, j, v) in has) == 1)

    return model, {"puzzle": puzzle}


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
