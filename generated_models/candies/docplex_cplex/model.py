# candies: a CPLEX (Python) model from DCP Rosetta.
# Download the `candies.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python candies.py candies.json

from docplex.mp.model import Model


def create_model(instance):
    """Candies: give every child at least one candy, more than any lower-rated neighbour, using as few candies as possible."""
    ratings = instance["ratings"]  # ratings[i]: the rating score of the i-th child in the line
    n = len(ratings)               # number of children

    model = Model("candies")

    # x[i] is the number of candies child i gets, at least 1. No child needs more than n: a
    # child gets one more than a lower-rated neighbour at most, and such a chain has at most n
    # children, so the bound cannot cut off an optimum.
    x = model.integer_var_list(n, 1, n, name="x")

    # Of two neighbours, the one with the higher rating gets more candies.
    model.add_constraints(x[i - 1] >= x[i] + 1 for i in range(1, n) if ratings[i - 1] > ratings[i])
    model.add_constraints(x[i] >= x[i - 1] + 1 for i in range(1, n) if ratings[i - 1] < ratings[i])

    # Minimise the total number of candies z.
    z = model.sum(x)
    model.minimize(z)

    return model, {"z": z, "x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
