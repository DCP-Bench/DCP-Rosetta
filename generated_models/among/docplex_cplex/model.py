# among: a CPLEX (Python) model from DCP Rosetta.
# Download the `among.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python among.py among.json

from docplex.mp.model import Model


def create_model(instance):
    """Among: choose n values in 0..7 such that exactly m of them are among the values of v."""
    n = instance["n"]  # the length of x
    m = instance["m"]  # how many entries of x take a value of v
    v = instance["v"]  # the values that are counted
    max_value = 7      # every entry of x lies between 0 and 7 (fixed by the problem statement)
    values = range(max_value + 1)
    positions = range(n)

    model = Model("among")

    # takes[i, a] is 1 when x[i] equals a
    takes = model.binary_var_matrix(positions, values, name="takes")

    # Each entry of x takes exactly one value.
    model.add_constraints(model.sum(takes[i, a] for a in values) == 1 for i in positions)

    # Exactly m entries of x take one of the values in v (a value of v outside 0..7 is never taken).
    counted = [a for a in values if a in v]
    model.add_constraint(model.sum(takes[i, a] for i in positions for a in counted) == m)

    # x[i] is the value of entry i
    x = [model.sum(a * takes[i, a] for a in values) for i in positions]
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
