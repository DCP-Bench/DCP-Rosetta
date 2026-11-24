# knapsack: a CPLEX (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python knapsack.py knapsack.json

from docplex.mp.model import Model


def create_model(instance):
    """0-1 knapsack: choose which items a hiker packs so that the total value is as large as possible
    without the total weight exceeding the backpack's capacity."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry
    n_items = len(values)

    model = Model("knapsack")

    # x[i] is 1 when the hiker packs item i, and 0 when not
    x = model.binary_var_list(n_items, name="x")

    # The packed items must not weigh more than the capacity.
    model.add_constraint(model.dot(x, weights) <= capacity)

    # Maximize the total value of the packed items.
    model.maximize(model.dot(x, values))

    return model, {"x": x}


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
