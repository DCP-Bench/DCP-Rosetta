# twelve_pack: a CPLEX (Python) model from DCP Rosetta.
# Download the `twelve_pack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python twelve_pack.py twelve_pack.json

from docplex.mp.model import Model


def create_model(instance):
    """Twelve pack: buy packs of the given sizes to get at least the target number of items, as few over it as possible."""
    packs = instance["packs"]    # packs[i]: the number of items in a pack of the i-th size
    target = instance["target"]  # the number of items wanted
    # A bound on each pack count, chosen to keep the variables finite: no optimal purchase needs more
    # than target packs of one size (dropping one would still reach the target), so 2 * target
    # cannot cut off an optimum.
    max_count = 2 * target

    model = Model("twelve_pack")

    # counts[i] is how many packs of the i-th size (packs[i] items each) are bought.
    counts = model.integer_var_list(len(packs), 0, max_count, name="counts")

    # The items bought are at least the target.
    items_bought = model.dot(counts, packs)
    model.add_constraint(items_bought >= target, ctname="enough")

    # Get as close to the target as possible, which means buying the fewest items.
    model.minimize(items_bought)

    return model, {"counts": counts}


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
