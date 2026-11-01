# best_host: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Run it (after `pip install ortools`) with:
#   python best_host.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Six guests sit around a round dinner table, and each guest will only sit next to
    two particular guests. Find a seating order in which every guest sits between two
    guests they accept."""
    n_guests = 6  # the number of guests

    # The guests.
    andrew, betty, cara, dave, erica, frank = range(n_guests)

    # prefs[g] lists the two guests that guest g will sit next to.
    prefs = [
        [dave, frank],    # Andrew
        [cara, erica],    # Betty
        [betty, frank],   # Cara
        [andrew, erica],  # Dave
        [betty, dave],    # Erica
        [andrew, cara],   # Frank
    ]

    model = cp_model.CpModel()

    # x[i] is the guest in seat i. The table is round, so the last seat is next to the first.
    x = [model.new_int_var(0, n_guests - 1, f"x{i}") for i in range(n_guests)]

    # Every guest has exactly one seat.
    model.add_all_different(x)

    # columns[j][g] is the j-th guest that guest g will sit next to.
    columns = [[prefs[guest][j] for guest in range(n_guests)] for j in range(2)]

    for i in range(n_guests):
        # allowed[j] is the j-th guest that the guest in seat i will sit next to, from the table.
        allowed = []
        for j in range(2):
            picked = model.new_int_var(0, n_guests - 1, f"allowed{i}_{j}")
            model.add_element(x[i], columns[j], picked)
            allowed.append(picked)

        # Both neighbours of seat i are among the two allowed guests.
        neighbours = [("prev", x[(i - 1) % n_guests]), ("next", x[(i + 1) % n_guests])]
        for side, neighbour in neighbours:
            # matches[j] is true when allowed guest j is this neighbour
            matches = []
            for j in range(2):
                same = model.new_bool_var(f"same{i}_{j}_{side}")
                model.add(allowed[j] == neighbour).only_enforce_if(same)
                model.add(allowed[j] != neighbour).only_enforce_if(~same)
                matches.append(same)
            model.add_bool_or(matches)

    return model, {"x": x}


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
