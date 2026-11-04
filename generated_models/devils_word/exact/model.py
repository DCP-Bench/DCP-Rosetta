# devils_word: an Exact (Python) model from DCP Rosetta.
# Download the `devils_word.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python devils_word.py devils_word.json

from exact import Exact


def create_model(instance):
    """Put a plus or a minus sign in front of each integer of the array so that
    the signed integers add up to the total."""
    arr = instance["arr"]      # arr[i]: the integer that gets a sign
    total = instance["total"]  # the value the signed integers must add up to
    n_ints = len(arr)          # the number of integers

    solver = Exact()

    # Exact identifies its variables by name.
    # plus[i] is 1 when arr[i] gets a plus sign, and 0 when it gets a minus sign
    plus = [f"plus_{i}" for i in range(n_ints)]
    # result[i] is arr[i] with its sign
    result = [f"result_{i}" for i in range(n_ints)]
    for i in range(n_ints):
        solver.addVariable(plus[i], 0, 1)
        solver.addVariable(result[i], -abs(arr[i]), abs(arr[i]))

    # Each integer is added or subtracted as its sign says.
    for i in range(n_ints):
        solver.addConstraint([(1, result[i]), (-2 * arr[i], plus[i])], True, -arr[i], True, -arr[i])

    # The signed integers add up to the total.
    solver.addConstraint([(1, name) for name in result], True, total, True, total)

    return solver, {"result": result}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
