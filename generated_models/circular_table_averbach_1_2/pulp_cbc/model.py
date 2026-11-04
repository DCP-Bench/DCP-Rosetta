# circular_table_averbach_1_2: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Run it (after `pip install pulp numpy`) with:
#   python circular_table_averbach_1_2.py

import pulp


def create_model(instance):
    """Three players, X, Y and Z, of different nationalities (American, English and French) sit
    round a circular table, each passing cards to the person on their right. Y passed three
    hearts to the American, and X passed to the person who passed to the Frenchwoman.
    Determine the nationality of each person."""
    n_seats = 3                                 # seats round the table, numbered 0, 1 and 2
    seats = range(n_seats)
    players = ["x", "y", "z"]                   # the three players
    nationalities = ["american", "english", "french"]

    problem = pulp.LpProblem("circular_table_averbach_1_2", pulp.LpMinimize)

    # in_seat[name][s] is 1 when the player or nationality name sits in seat s, and 0 when not
    in_seat = {
        name: {s: pulp.LpVariable(f"in_seat_{name}_{s}", cat="Binary") for s in seats}
        for name in players + nationalities
    }

    # Each player and each nationality sits in exactly one seat.
    for name in players + nationalities:
        problem += pulp.lpSum(in_seat[name].values()) == 1

    # Each seat holds exactly one player and exactly one nationality.
    for group in (players, nationalities):
        for s in seats:
            problem += pulp.lpSum(in_seat[name][s] for name in group) == 1

    # Seat 1 is to the right of seat 0, seat 2 to the right of seat 1, and seat 0 to the right of seat 2.
    # Y passed three hearts to the American, so the American sits to the right of Y.
    for s in seats:
        problem += in_seat["american"][(s + 1) % n_seats] == in_seat["y"][s]

    # X passed cards to the person who passed cards to the Frenchwoman, so X sits to the right
    # of the Frenchwoman.
    for s in seats:
        problem += in_seat["x"][(s + 1) % n_seats] == in_seat["french"][s]

    # seat[name] is the seat number of the player or nationality name.
    seat = {name: pulp.lpSum(s * in_seat[name][s] for s in seats) for name in in_seat}

    return problem, seat


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
