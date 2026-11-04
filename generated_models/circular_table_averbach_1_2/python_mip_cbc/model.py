# circular_table_averbach_1_2: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Run it (after `pip install mip numpy`) with:
#   python circular_table_averbach_1_2.py

import mip


def create_model(instance):
    """Three players, X, Y and Z, of different nationalities (American, English and French) sit around
    a round table, each passing three cards to the person on their right. Y passed three hearts to the
    American, and X passed cards to the person who passed to the Frenchwoman. Find the seat of each
    player and of each nationality."""
    # The seats around the table, numbered 0 to 2. Seat 1 is on the right of seat 0, seat 2 on the
    # right of seat 1, and seat 0 on the right of seat 2.
    n_seats = 3
    players = ["x", "y", "z"]  # the players X, Y and Z
    nationalities = ["american", "english", "french"]
    names = players + nationalities

    model = mip.Model(solver_name="CBC")

    # seat[name] is the seat of the player or nationality called name
    seat = {}
    # sits_at[name][s] is 1 when that player or nationality sits in seat s, and 0 when not
    sits_at = {}
    for name in names:
        seat[name] = model.add_var(name, var_type=mip.INTEGER, lb=0, ub=n_seats - 1)
        sits_at[name] = [model.add_var(f"{name}_at_{s}", var_type=mip.BINARY) for s in range(n_seats)]

    # Each player and each nationality sits in exactly one seat.
    for name in names:
        model += mip.xsum(sits_at[name]) == 1

    # The seat of each player and nationality is the seat it sits in.
    for name in names:
        model += seat[name] == mip.xsum(s * sits_at[name][s] for s in range(n_seats))

    # Each seat holds exactly one player and exactly one nationality.
    for s in range(n_seats):
        model += mip.xsum(sits_at[p][s] for p in players) == 1
        model += mip.xsum(sits_at[n][s] for n in nationalities) == 1

    # Y passed three hearts to the American, so the American sits on Y's right.
    for s in range(n_seats):
        model += sits_at["american"][(s + 1) % n_seats] == sits_at["y"][s]

    # X passed cards to the person who passed to the Frenchwoman, so the Frenchwoman sits two seats
    # to the right of X.
    for s in range(n_seats):
        model += sits_at["french"][(s + 2) % n_seats] == sits_at["x"][s]

    return model, seat


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
