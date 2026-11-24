# cutting_stock: a CPLEX (Python) model from DCP Rosetta.
# Download the `cutting_stock.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python cutting_stock.py cutting_stock.json

from docplex.mp.model import Model


def create_model(instance):
    """Cutting stock: choose how often to cut each pattern so every order is met with as few raw rolls as possible."""
    pieces = instance["num_rolls_width"]  # pieces[p][w]: pieces of width w one cut of pattern p yields
    orders = instance["orders"]  # orders[w]: the number of pieces of width w that are needed
    patterns = range(instance["num_patterns"])
    widths = range(len(instance["widths"]))  # the piece widths, by index

    model = Model("cutting_stock")

    # patterns_used[p] is how many raw rolls are cut with pattern p. The bound is not in the
    # statement: cutting one roll per ordered piece already meets every order, so an optimal plan
    # never cuts more than sum(orders) rolls and no optimum is lost.
    max_rolls = sum(orders)
    patterns_used = model.integer_var_list(instance["num_patterns"], 0, max_rolls, name="patterns_used")

    # For each width, the pieces cut meet the number ordered.
    for w in widths:
        model.add_constraint(model.sum(pieces[p][w] * patterns_used[p] for p in patterns) >= orders[w],
                             ctname=f"order_{w}")

    # Minimise the number of raw rolls cut.
    min_rolls_cut = model.sum(patterns_used)
    model.minimize(min_rolls_cut)

    return model, {"patterns_used": patterns_used, "min_rolls_cut": min_rolls_cut}


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
