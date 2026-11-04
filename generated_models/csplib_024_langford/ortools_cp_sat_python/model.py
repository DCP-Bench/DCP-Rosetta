# csplib_024_langford: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_024_langford.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_024_langford.py csplib_024_langford.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Arrange two copies of each number from 1 to k into one sequence of 2k numbers, so that the
    two 1's appear one number apart, the two 2's two numbers apart, ..., and the two k's k numbers
    apart."""
    k = instance["k"]  # the largest number in the sequence

    model = cp_model.CpModel()

    # The place in the sequence of each copy of each number.
    position = [model.new_int_var(0, 2 * k - 1, f"position_{j}") for j in range(2 * k)]

    # sol[p] is the number at place p of the sequence
    sol = [model.new_int_var(1, k, f"sol_{p}") for p in range(2 * k)]

    # Every copy has its own place, so every place of the sequence holds exactly one copy.
    model.add_all_different(position)

    for i in range(1, k + 1):
        # The two copies of i have i numbers between them.
        model.add(position[k + i - 1] == position[i - 1] + i + 1)
        # Number i is at both of its places in the sequence.
        model.add_element(position[i - 1], sol, i)
        model.add_element(position[k + i - 1], sol, i)

    return model, {"sol": sol}


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
