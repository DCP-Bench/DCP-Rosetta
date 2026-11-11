# bowls_and_oranges: a CPLEX (Python) model from DCP Rosetta.
# Download the `bowls_and_oranges.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python bowls_and_oranges.py bowls_and_oranges.json

from docplex.mp.model import Model


def create_model(instance):
    """Bowls and oranges: put m oranges in distinct bowls 1..n so that no three are evenly spaced."""
    n = instance["n"]  # number of bowls, numbered 1..n
    m = instance["m"]  # number of oranges to place

    model = Model("bowls_and_oranges")

    # x[i] is the bowl of the i-th orange. The bowls are listed in ascending order, which also
    # puts at most one orange in each bowl.
    x = model.integer_var_list(m, 1, n, name="x")
    model.add_constraints(x[i] >= x[i - 1] + 1 for i in range(1, m))

    # No three oranges A, B, C (taken in ascending order) have the distance from A to B equal to
    # the distance from B to C.
    model.add_constraints(x[b] - x[a] != x[c] - x[b]
                          for a in range(m) for b in range(a + 1, m) for c in range(b + 1, m))

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
