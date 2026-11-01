# csplib_019_magic_squares_and_sequences: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_019_magic_squares_and_sequences.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_019_magic_squares_and_sequences.py csplib_019_magic_squares_and_sequences.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A magic sequence of length n is a sequence of integers x_0, ..., x_{n-1}
    between 0 and n-1 such that, for every i, the number i occurs exactly x_i times
    in the sequence."""
    n_positions = instance["n"]  # the length of the sequence

    model = cp_model.CpModel()

    # x[i] is the number at position i, so it is also how often the number i occurs
    x = [model.new_int_var(0, n_positions - 1, f"x_{i}") for i in range(n_positions)]

    # is_value[i][v] is true when x[i] equals v
    is_value = [[model.new_bool_var(f"is_{i}_{v}") for v in range(n_positions)]
                for i in range(n_positions)]
    # Each position takes exactly one value, the one flagged in is_value.
    for i in range(n_positions):
        for v in range(n_positions):
            model.add(x[i] == v).only_enforce_if(is_value[i][v])
            model.add(x[i] != v).only_enforce_if(~is_value[i][v])
        model.add_exactly_one(is_value[i])

    # The number v occurs exactly x[v] times: x[v] counts the positions that hold v.
    for v in range(n_positions):
        model.add(x[v] == sum(is_value[i][v] for i in range(n_positions)))

    return model, {"x": x}


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
