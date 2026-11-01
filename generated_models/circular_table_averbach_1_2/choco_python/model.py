# circular_table_averbach_1_2: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Run it (after `pip install pychoco numpy`) with:
#   python circular_table_averbach_1_2.py

from pychoco.model import Model


def create_model(instance):
    """Three players of different nationalities sit round a circular table, and each passes three
    cards to the person on their right. Work out who is who from what Y and X passed."""
    n_seats = 3  # the seats round the table, numbered 0, 1 and 2, each on the right of the one before

    model = Model()

    # seat a is on the right of seat b
    def right_of(a, b):
        # the seat after b, numbered 1 to 3 so that the seat after seat 2 is seat 0 again
        next_seat = model.intvar(1, n_seats, name="next_seat")
        model.arithm(b, "+", 1, "=", next_seat).post()
        model.mod(next_seat, n_seats, a).post()

    # x, y, z: the seat of X, Y and Z
    x = model.intvar(0, n_seats - 1, name="x")
    y = model.intvar(0, n_seats - 1, name="y")
    z = model.intvar(0, n_seats - 1, name="z")
    # The three players sit in different seats.
    model.all_different([x, y, z]).post()

    # american, english, french: the seat of the American, the English player and the Frenchwoman
    american = model.intvar(0, n_seats - 1, name="american")
    english = model.intvar(0, n_seats - 1, name="english")
    french = model.intvar(0, n_seats - 1, name="french")
    # The three nationalities sit in different seats.
    model.all_different([american, english, french]).post()

    # The American sits on Y's right, since Y passed three hearts to the American.
    right_of(american, y)
    # X sits on the Frenchwoman's right, since X passed to the person who passed to her.
    right_of(x, french)

    return model, {
        "x": x, "y": y, "z": z, "american": american, "english": english, "french": french,
    }, None


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
