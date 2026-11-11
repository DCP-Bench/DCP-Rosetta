# fifty_puzzle: a CPLEX (Python) model from DCP Rosetta.
# Download the `fifty_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python fifty_puzzle.py fifty_puzzle.json

from docplex.mp.model import Model


def create_model(instance):
    """Choose which dummies to knock over with baseballs so that the numbers on the knocked-over
    dummies add up to exactly the target sum, neither more nor less."""
    values = instance["values"]          # values[i]: the number on dummy i
    target_sum = instance["target_sum"]  # the sum the knocked-over dummies must reach exactly

    model = Model("fifty_puzzle")

    # dummies[i] is 1 when dummy i is knocked over.
    dummies = model.binary_var_list(len(values), name="dummies")

    # The numbers on the knocked-over dummies add up to the target, neither more nor less.
    model.add_constraint(model.dot(dummies, values) == target_sum, ctname="target")

    return model, {"dummies": dummies}


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
