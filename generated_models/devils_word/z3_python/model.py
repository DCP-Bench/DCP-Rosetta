# devils_word: a Z3 (Python) model from DCP Rosetta.
# Download the `devils_word.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python devils_word.py devils_word.json

import z3


def create_model(instance):
    """Given a list of integers, put a plus or a minus sign in front of each one
    so that the signed integers add up to the given total."""
    arr = instance["arr"]      # the integers, in order
    total = instance["total"]  # the value the signed integers must add up to

    # result[i] is arr[i] with the sign it gets
    result = [z3.Int(f"result_{i}") for i in range(len(arr))]

    solver = z3.Solver()

    # Each integer is added or subtracted.
    solver.add([z3.Or(result[i] == value, result[i] == -value) for i, value in enumerate(arr)])

    # The signed integers add up to the total.
    solver.add(z3.Sum(result) == total)

    return solver, {"result": result}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
