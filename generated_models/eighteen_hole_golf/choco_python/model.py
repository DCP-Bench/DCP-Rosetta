# eighteen_hole_golf: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Run it (after `pip install pychoco numpy`) with:
#   python eighteen_hole_golf.py

from pychoco.model import Model


def create_model(instance):
    """Lay out a golf course of 18 holes, each 3, 4 or 5 long, whose lengths
    add up to 72."""
    n_holes = 18        # the course has 18 holes
    total_length = 72   # the total length of the course

    model = Model()

    # holes[i] is the length of hole i, 3, 4 or 5
    holes = [model.intvar(3, 5, name=f"holes_{i}") for i in range(n_holes)]

    # The lengths of the holes add up to the total length.
    model.sum(holes, "=", total_length).post()

    return model, {"holes": holes}, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
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
