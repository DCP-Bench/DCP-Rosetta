# best_host: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Run it (after `pip install mip numpy`) with:
#   python best_host.py

import mip


def create_model(instance):
    """Seat six guests around a round dinner table so that every guest sits next to
    only guests on their list. Each guest will sit next to just two particular guests."""
    # neighbours[g] lists the two guests that guest g will sit next to.
    neighbours = {
        0: [3, 5],  # Andrew: Dave and Frank
        1: [2, 4],  # Betty: Cara and Erica
        2: [1, 5],  # Cara: Betty and Frank
        3: [0, 4],  # Dave: Andrew and Erica
        4: [1, 3],  # Erica: Betty and Dave
        5: [0, 2],  # Frank: Andrew and Cara
    }
    n_guests = len(neighbours)  # the number of guests, which is also the number of seats

    model = mip.Model(solver_name="CBC")

    # seat[i][g] is 1 when guest g sits in seat i, and 0 otherwise.
    seat = [[model.add_var(f"seat_{i}_{g}", var_type=mip.BINARY) for g in range(n_guests)]
            for i in range(n_guests)]

    # Each seat holds exactly one guest.
    for i in range(n_guests):
        model += mip.xsum(seat[i][g] for g in range(n_guests)) == 1

    # Each guest sits in exactly one seat.
    for g in range(n_guests):
        model += mip.xsum(seat[i][g] for i in range(n_guests)) == 1

    # The table is round, so the last seat is next to the first.
    # The guest next to a guest g must be on g's list.
    for i in range(n_guests):
        j = (i + 1) % n_guests
        for g in range(n_guests):
            model += mip.xsum(seat[j][h] for h in neighbours[g]) >= seat[i][g]

    # x[i] is the number of the guest in seat i.
    x = [mip.xsum(g * seat[i][g] for g in range(n_guests)) for i in range(n_guests)]

    return model, {"x": x}


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
