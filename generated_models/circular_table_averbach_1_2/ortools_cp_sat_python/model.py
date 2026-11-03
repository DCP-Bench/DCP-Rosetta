# circular_table_averbach_1_2: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Run it (after `pip install ortools`) with:
#   python circular_table_averbach_1_2.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Three players, X, Y and Z, of different nationalities (American, English and French)
    sit round a circular table, each passing cards to the person on their right. Y passed
    three hearts to the American, and X passed to the person who passed to the Frenchwoman.
    Determine the nationality of each person."""
    n_seats = 3  # the seats around the table

    model = cp_model.CpModel()

    # x, y, z: the seat of X, Y and Z
    x, y, z = (model.new_int_var(0, n_seats - 1, name) for name in "xyz")
    # X, Y and Z sit in different seats.
    model.add_all_different([x, y, z])

    # american, english, french: the seat of the American, the English and the French player
    american, english, french = (
        model.new_int_var(0, n_seats - 1, name) for name in ("american", "english", "french")
    )
    # The American, the English and the French player sit in different seats.
    model.add_all_different([american, english, french])

    # a is the seat immediately to the right of seat b.
    def right_of(a, b):
        model.add_modulo_equality(a, b + 1, n_seats)

    # The American sits to the right of Y.
    right_of(american, y)
    # X sits to the right of the Frenchwoman.
    right_of(x, french)

    return model, {
        "x": x,
        "y": y,
        "z": z,
        "american": american,
        "english": english,
        "french": french,
    }


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
