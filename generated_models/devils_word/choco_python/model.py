# devils_word: a Choco-solver (Python) model from DCP Rosetta.
# Download the `devils_word.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python devils_word.py devils_word.json

from pychoco.model import Model


def create_model(instance):
    """Given an array of integers, put a plus or a minus sign in front of each
    integer so that the signed integers add up to the given total."""
    arr = instance["arr"]      # arr[i]: the integer that gets a sign
    total = instance["total"]  # the value the signed integers must add up to

    model = Model()

    # result[i] is arr[i] with its sign, so it is arr[i] or -arr[i]; a zero stays zero
    result = []
    for i, value in enumerate(arr):
        if value == 0:
            result.append(model.intvar(0, 0, name=f"result_{i}"))
        else:
            result.append(model.intvar([-abs(value), abs(value)], name=f"result_{i}"))

    # The signed integers add up to the total.
    model.sum(result, "=", total).post()

    return model, {"result": result}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
