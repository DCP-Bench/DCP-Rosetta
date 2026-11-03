# clock_triplets: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Run it (after `pip install pychoco numpy`) with:
#   python clock_triplets.py

from pychoco.model import Model


def create_model(instance):
    """Rearrange the numbers 1 to 12 around a clock face so that no three adjacent
    numbers sum to more than 21, the smallest value the largest such sum can take."""
    n_numbers = 12  # numbers on the clock face

    model = Model()

    # x[i] is the number at position i of the clock face
    x = [model.intvar(1, n_numbers, name=f"x{i}") for i in range(n_numbers)]

    # Each number from 1 to 12 appears once on the clock.
    model.all_different(x).post()

    # Every three adjacent numbers, wrapping around the face, sum to at most 21.
    for i in range(n_numbers):
        trio = [x[i], x[(i - 1) % n_numbers], x[(i - 2) % n_numbers]]
        model.scalar(trio, [1, 1, 1], "<=", 21).post()

    return model, {"x": x}, None


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
