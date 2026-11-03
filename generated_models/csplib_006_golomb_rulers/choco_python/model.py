# csplib_006_golomb_rulers: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_006_golomb_rulers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_006_golomb_rulers.py csplib_006_golomb_rulers.json

from pychoco.model import Model


def create_model(instance):
    """Golomb ruler: place n_marks marks at whole-number positions on a ruler, the first at 0,
    so that the distances between every pair of marks are all different. Find the shortest
    such ruler, where the length is the position of the last mark."""
    n_marks = instance["size"]  # the number of marks on the ruler

    model = Model()

    # marks[i] is the position of mark i, at most n_marks * n_marks from the start.
    # The first mark is at position 0.
    marks = [model.intvar(0, 0, name="marks_0")] + [
        model.intvar(0, n_marks * n_marks, name=f"marks_{i}") for i in range(1, n_marks)
    ]

    # The marks lie in order along the ruler.
    for i in range(n_marks - 1):
        model.arithm(marks[i], "<", marks[i + 1]).post()

    # differences holds the distance between each pair of marks.
    differences = []
    for i in range(n_marks - 1):
        for j in range(i + 1, n_marks):
            difference = model.intvar(1, n_marks * n_marks, name=f"difference_{i}_{j}")
            model.arithm(marks[j], "-", marks[i], "=", difference).post()
            differences.append(difference)

    # No two pairs of marks are the same distance apart.
    model.all_different(differences).post()

    # The length of the ruler is the position of its last mark, to be as small as possible.
    length = marks[n_marks - 1]

    return model, {"marks": marks, "length": length}, {"objective": length, "maximize": False}


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
