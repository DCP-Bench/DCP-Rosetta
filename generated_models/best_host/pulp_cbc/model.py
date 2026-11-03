# best_host: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Run it (after `pip install pulp numpy`) with:
#   python best_host.py

import pulp


def create_model(instance):
    """Seat six guests around a round dinner table so that every guest sits only next to
    the two guests they get along with."""
    n = 6  # the number of guests, and of seats

    # The guests are numbered 0 to 5 in this order.
    andrew, betty, cara, dave, erica, frank = range(n)

    # prefs[g] lists the two guests that guest g will sit next to.
    prefs = [
        [dave, frank],    # Andrew
        [cara, erica],    # Betty
        [betty, frank],   # Cara
        [andrew, erica],  # Dave
        [betty, dave],    # Erica
        [andrew, cara],   # Frank
    ]

    seats = range(n)  # seat 0 is next to seat n - 1, the table being round
    guests = range(n)

    problem = pulp.LpProblem("best_host", pulp.LpMinimize)

    # sit[i][g] is 1 when guest g sits in seat i, and 0 when not
    sit = [[pulp.LpVariable(f"sit_{i}_{g}", cat="Binary") for g in guests] for i in seats]

    # Every seat holds one guest.
    for i in seats:
        problem += pulp.lpSum(sit[i]) == 1

    # Every guest has one seat.
    for g in guests:
        problem += pulp.lpSum(sit[i][g] for i in seats) == 1

    # Two guests who do not both accept each other never sit in neighbouring seats.
    for i in seats:
        j = (i + 1) % n  # the seat after seat i
        for g in guests:
            for h in guests:
                if h != g and (h not in prefs[g] or g not in prefs[h]):
                    problem += sit[i][g] + sit[j][h] <= 1

    # x[i] is the guest in seat i, numbered as above.
    x = [pulp.lpSum(g * sit[i][g] for g in guests) for i in seats]

    return problem, {"x": x}


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
