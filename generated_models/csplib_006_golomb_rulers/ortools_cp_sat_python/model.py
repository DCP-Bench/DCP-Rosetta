# csplib_006_golomb_rulers: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_006_golomb_rulers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_006_golomb_rulers.py csplib_006_golomb_rulers.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Place marks on a ruler, the first at position 0, so that the differences between
    all pairs of marks are distinct. Find the shortest such Golomb ruler."""
    size = instance["size"]  # the number of marks on the ruler

    model = cp_model.CpModel()

    # marks[i] is the position of mark i on the ruler. The first mark is at position 0.
    marks = [model.new_int_var(0, 0, "marks_0")] + [
        model.new_int_var(0, size * size, f"marks_{i}") for i in range(1, size)
    ]
    # length is the length of the ruler, the position of its last mark
    length = marks[size - 1]

    # The marks are placed in strictly increasing order of position.
    for i in range(size - 1):
        model.add(marks[i] < marks[i + 1])
    # Golomb condition: the differences between all pairs of marks are distinct.
    differences = [marks[j] - marks[i] for i in range(size - 1) for j in range(i + 1, size)]
    model.add_all_different(differences)

    # The objective is to minimise the length of the ruler.
    model.minimize(length)

    return model, {"marks": marks, "length": length}


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
