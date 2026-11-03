# csplib_039_rehearsal: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_039_rehearsal.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_039_rehearsal.py csplib_039_rehearsal.json

import mip


def create_model(instance):
    """A concert has pieces of different durations, each played by a combination of orchestra
    players. A player arrives just before the first piece they play and leaves just after the last.
    Order the pieces for rehearsal so that the players spend as little time as possible present but
    not playing."""
    n_pieces = instance["num_pieces"]    # the number of pieces
    n_players = instance["num_players"]  # the number of players
    duration = instance["duration"]      # duration[q]: the length of piece q
    rehearsal = instance["rehearsal"]    # rehearsal[p][q] is 1 when player p plays in piece q
    total = sum(duration)                # the length of the whole concert

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # before[i][j] is 1 when piece i is rehearsed before piece j
    before = [[None] * n_pieces for _ in range(n_pieces)]
    for i in range(n_pieces):
        for j in range(n_pieces):
            if i != j:
                before[i][j] = model.add_var(f"before_{i}_{j}", var_type=mip.BINARY)

    # Of two pieces, exactly one is rehearsed first.
    for i in range(n_pieces):
        for j in range(i + 1, n_pieces):
            model += before[i][j] + before[j][i] == 1

    # No three pieces come before each other in a cycle.
    for i in range(n_pieces):
        for j in range(n_pieces):
            for k in range(n_pieces):
                if len({i, j, k}) == 3:
                    model += before[i][j] + before[j][k] + before[k][i] <= 2

    # start[i] is the time piece i starts: the durations of the pieces rehearsed before it.
    start = [
        mip.xsum(duration[j] * before[j][i] for j in range(n_pieces) if j != i)
        for i in range(n_pieces)
    ]

    # x[i][s] is 1 when piece i is rehearsed in slot s
    x = [[model.add_var(f"x_{i}_{s}", var_type=mip.BINARY) for s in range(n_pieces)]
         for i in range(n_pieces)]

    # Each piece takes one slot, and its slot number is the count of pieces rehearsed before it.
    for i in range(n_pieces):
        model += mip.xsum(x[i][s] for s in range(n_pieces)) == 1
        model += (mip.xsum(before[j][i] for j in range(n_pieces) if j != i)
                  == mip.xsum(s * x[i][s] for s in range(n_pieces)))

    # Each slot holds one piece.
    for s in range(n_pieces):
        model += mip.xsum(x[i][s] for i in range(n_pieces)) == 1

    # rehearsal_order[s] is the piece rehearsed in slot s
    rehearsal_order = [model.add_var(f"order_{s}", lb=0, ub=n_pieces - 1, var_type=mip.INTEGER)
                       for s in range(n_pieces)]
    for s in range(n_pieces):
        model += rehearsal_order[s] == mip.xsum(i * x[i][s] for i in range(n_pieces))

    # presence collects the time each player is present: from arrive to depart.
    presence = []
    for p in range(n_players):
        played = [i for i in range(n_pieces) if rehearsal[p][i]]
        if not played:
            # a player who plays no piece is never present
            continue

        # arrive and depart are the times player p arrives and leaves, within the concert.
        arrive = model.add_var(f"arrive_{p}", lb=0, ub=total, var_type=mip.INTEGER)
        depart = model.add_var(f"depart_{p}", lb=0, ub=total, var_type=mip.INTEGER)

        # The player arrives before each piece they play.
        for i in played:
            model += arrive <= start[i]

        # The player stays until each piece they play is over.
        for i in played:
            model += depart >= start[i] + duration[i]

        presence.append(depart - arrive)

    # Minimise the total time the players are present. Their playing time is the same for every
    # order, so this also minimises the time they wait.
    model.objective = mip.xsum(presence)

    return model, {"rehearsal_order": rehearsal_order}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
