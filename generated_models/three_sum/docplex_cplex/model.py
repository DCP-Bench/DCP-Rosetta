# three_sum: a CPLEX (Python) model from DCP Rosetta.
# Download the `three_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python three_sum.py three_sum.json

from docplex.mp.model import Model


def create_model(instance):
    """Zero sum: select exactly m of the numbers so that they add up to zero."""
    nums = instance["nums"]  # nums[i]: the i-th integer of the collection
    m = instance["m"]        # how many elements must be selected

    model = Model("three_sum")

    # indices[i] is 1 when nums[i] is selected.
    indices = model.binary_var_list(len(nums), name="indices")

    # The selected numbers add up to zero.
    model.add_constraint(model.dot(indices, nums) == 0, ctname="zero_sum")

    # Exactly m numbers are selected.
    model.add_constraint(model.sum(indices) == m, ctname="count")

    return model, {"indices": indices}


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
