# csplib_007_all_interval: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_007_all_interval.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_007_all_interval.py csplib_007_all_interval.json

from pychoco.model import Model


def create_model(instance):
    """All-interval series: arrange the pitch classes 0 to n_notes - 1, each once, in a row so
    that the distances between neighbouring pitch classes are all different and cover every
    distance from 1 to n_notes - 1."""
    n_notes = instance["n"]  # the number of pitch classes, and so of notes in the series

    model = Model()

    # x[i] is the pitch class of the note at position i
    x = [model.intvar(0, n_notes - 1, name=f"x{i}") for i in range(n_notes)]

    # diffs[i] is the distance between the notes at positions i and i + 1
    diffs = [model.intvar(1, n_notes - 1, name=f"diffs{i}") for i in range(n_notes - 1)]

    # Each pitch class occurs once in the series.
    model.all_different(x).post()

    # Each distance from 1 to n_notes - 1 occurs once between neighbouring notes.
    model.all_different(diffs).post()

    # Each distance is the gap between the pitch classes of two neighbouring notes.
    for i in range(n_notes - 1):
        model.distance(x[i + 1], x[i], "=", diffs[i]).post()

    return model, {"x": x, "diffs": diffs}, None


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
