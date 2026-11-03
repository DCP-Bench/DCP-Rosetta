# devils_word: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `devils_word.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
# Then run it on the first instance (after `pip install ortools`):
#   python devils_word.py devils_word.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Given an array of integers, put a plus or a minus sign in front of each
    integer so that the signed integers add up to the given total."""
    arr = instance["arr"]      # arr[i]: the integer that gets a sign
    total = instance["total"]  # the value the signed integers must add up to
    n_ints = len(arr)          # the number of integers
    max_val = max(arr)         # the largest integer, which bounds the size of each signed integer

    model = cp_model.CpModel()

    # plus[i] is true when arr[i] gets a plus sign and false when it gets a minus sign
    plus = [model.new_bool_var(f"plus_{i}") for i in range(n_ints)]
    # result[i] is arr[i] with its sign
    result = [model.new_int_var(-max_val, max_val, f"result_{i}") for i in range(n_ints)]

    # Each integer is added when its sign is plus and subtracted when it is minus.
    for i in range(n_ints):
        model.add(result[i] == arr[i]).only_enforce_if(plus[i])
        model.add(result[i] == -arr[i]).only_enforce_if(~plus[i])

    # The signed integers add up to the total.
    model.add(sum(result) == total)

    return model, {"result": result}


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
