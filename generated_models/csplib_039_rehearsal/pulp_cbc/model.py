# csplib_039_rehearsal: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_039_rehearsal.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_039_rehearsal.py csplib_039_rehearsal.json

import pulp


def create_model(instance):
    """A concert consists of pieces of different durations, each played by a different combination
    of orchestra members. A player arrives just before the first piece they play in and leaves
    just after the last. Order the pieces for rehearsal so that the total time players spend
    present but not playing is as small as possible."""
    n_pieces = instance["num_pieces"]      # number of pieces
    n_players = instance["num_players"]    # number of players
    duration = instance["duration"]        # duration[i]: length of piece i
    plays = instance["rehearsal"]          # plays[p][i] is 1 when player p plays in piece i

    problem = pulp.LpProblem("rehearsal", pulp.LpMinimize)

    # pos[i][t] is 1 when piece i is rehearsed in slot t
    pos = [[pulp.LpVariable(f"pos_{i}_{t}", cat="Binary") for t in range(n_pieces)]
           for i in range(n_pieces)]

    # Each piece is rehearsed in one slot, and each slot holds one piece.
    for i in range(n_pieces):
        problem += pulp.lpSum(pos[i]) == 1
    for t in range(n_pieces):
        problem += pulp.lpSum(pos[i][t] for i in range(n_pieces)) == 1

    # rehearsal_order[t] is the piece rehearsed in slot t
    rehearsal_order = [pulp.lpSum(i * pos[i][t] for i in range(n_pieces))
                       for t in range(n_pieces)]

    # before[(j, i)] is 1 when piece j is rehearsed before piece i. Every two pieces are
    # ordered one way or the other.
    before = {(j, i): pulp.LpVariable(f"before_{j}_{i}", cat="Binary")
              for i in range(n_pieces) for j in range(n_pieces) if i != j}
    for i in range(n_pieces):
        for j in range(i + 1, n_pieces):
            problem += before[(i, j)] + before[(j, i)] == 1
        # The slot of piece i is the number of pieces rehearsed before it.
        problem += pulp.lpSum(t * pos[i][t] for t in range(n_pieces)) == pulp.lpSum(
            before[(j, i)] for j in range(n_pieces) if j != i)

    # start[i] is when piece i starts: the durations of the pieces rehearsed before it.
    start = [pulp.lpSum(duration[j] * before[(j, i)] for j in range(n_pieces) if j != i)
             for i in range(n_pieces)]

    # The rehearsal lasts no longer than all the pieces together.
    horizon = sum(duration)
    # cost_terms[k] is the time player k is present, and fixed_playing_time the time all
    # players spend playing.
    cost_terms = []
    fixed_playing_time = 0
    for p in range(n_players):
        pieces = [i for i in range(n_pieces) if plays[p][i] == 1]
        if not pieces:
            continue  # a player who plays nothing never waits

        # arrival[p] is when player p arrives and departure[p] when they leave.
        arrival = pulp.LpVariable(f"arrival_{p}", 0, horizon, cat="Continuous")
        departure = pulp.LpVariable(f"departure_{p}", 0, horizon, cat="Continuous")
        # Player p arrives no later than the start of each piece they play, and leaves no earlier
        # than its end. Minimizing pulls them onto the first start and the last end.
        for i in pieces:
            problem += arrival <= start[i]
            problem += departure >= start[i] + duration[i]

        cost_terms.append(departure - arrival)
        fixed_playing_time += sum(duration[i] for i in pieces)

    # Minimize the total waiting time: the time players are present minus the time they play.
    problem += pulp.lpSum(cost_terms) - fixed_playing_time

    return problem, {"rehearsal_order": rehearsal_order}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
