# devils_word: a cvc5 (Python) model from DCP Rosetta.
# Download the `devils_word.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python devils_word.py devils_word.json

import cvc5.pythonic as c5


def create_model(instance):
    """Given an array of integers, put a plus or a minus sign in front of each
    integer so that the signed integers add up to the given total."""
    arr = instance["arr"]      # arr[i]: the integer that gets a sign
    total = instance["total"]  # the value the signed integers must add up to

    # result[i] is arr[i] with its sign
    result = [c5.Int(f"result_{i}") for i in range(len(arr))]

    solver = c5.Solver()

    # Each integer is added or subtracted.
    solver.add([c5.Or(r == a, r == -a) for r, a in zip(result, arr)])

    # The signed integers add up to the total.
    solver.add(c5.Sum(result) == total)

    return solver, {"result": result}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
