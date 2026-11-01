# best_host: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Run it (after `pip install pychoco numpy`) with:
#   python best_host.py

from pychoco.model import Model


def create_model(instance):
    """Six guests sit around a round dinner table, and each guest will only sit next to
    two particular guests. Find a seating order in which every guest sits between two
    guests they accept."""
    n_guests = 6
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

    # the pairs of guests who each accept the other
    good_neighbours = [(a, b) for a in range(n_guests) for b in range(n_guests)
                       if b in prefs[a] and a in prefs[b]]

    model = Model()

    # x[i] is the guest in seat i; the table is round, so the last seat is next to the first
    x = [model.intvar(0, n_guests - 1, name=f"x_{i}") for i in range(n_guests)]

    # Every guest has exactly one seat.
    model.all_different(x).post()

    # Each guest sits next to two guests who accept them.
    for i in range(n_guests):
        model.table([x[i], x[(i + 1) % n_guests]], good_neighbours).post()

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
