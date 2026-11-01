# fifty_puzzle: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `fifty_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Then run it on the first instance (after `pip install ortools`):
#   python fifty_puzzle.py fifty_puzzle.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Dummies numbered with integers are to be knocked over with baseballs:
    choose the dummies to knock down so that their numbers add up to exactly
    the target sum, neither more nor less."""
    values = instance["values"]          # values[i]: the number on dummy i
    target_sum = instance["target_sum"]  # the sum the knocked-over numbers must reach

    model = cp_model.CpModel()

    # dummies[i] is true when dummy i is knocked over
    dummies = [model.new_bool_var(f"dummies_{i}") for i in range(len(values))]

    # The numbers on the knocked-over dummies add up to exactly the target sum.
    model.add(sum(v * d for v, d in zip(values, dummies)) == target_sum)

    return model, {"dummies": dummies}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
