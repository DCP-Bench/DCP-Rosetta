# csplib_019_magic_squares_and_sequences: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_019_magic_squares_and_sequences.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_019_magic_squares_and_sequences.py csplib_019_magic_squares_and_sequences.json

from pychoco.model import Model


def create_model(instance):
    """A magic sequence of length n is a sequence of integers x_0, ..., x_{n-1}
    between 0 and n-1 such that, for every i, the number i occurs exactly x_i times
    in the sequence."""
    n_positions = instance["n"]  # the length of the sequence

    model = Model()

    # The number at each position of the sequence.
    x = [model.intvar(0, n_positions - 1, name=f"x_{i}") for i in range(n_positions)]

    # The number i occurs exactly x[i] times in the sequence.
    for i in range(n_positions):
        model.count(i, x, x[i]).post()

    return model, {"x": x}, None


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
