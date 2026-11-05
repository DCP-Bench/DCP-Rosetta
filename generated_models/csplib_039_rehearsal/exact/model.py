# csplib_039_rehearsal: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_039_rehearsal.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_039_rehearsal.py csplib_039_rehearsal.json

from exact import Exact


def create_model(instance):
    """A concert has pieces of different durations, each played by a different group of players.
    A player arrives just before the first piece they play in and leaves just after the last one.
    Order the pieces for rehearsal so that the total time the players spend present but not
    playing is as small as possible."""
    n_pieces = instance["num_pieces"]    # the number of pieces
    n_players = instance["num_players"]  # the number of players
    duration = instance["duration"]      # duration[i]: how long piece i lasts
    rehearsal = instance["rehearsal"]    # rehearsal[p][i] is 1 when player p plays in piece i
    total_time = sum(duration)           # the whole rehearsal lasts this long, so no time falls after it

    solver = Exact()

    # Exact identifies its variables by name.
    # at_slot[i][s] is 1 when piece i is rehearsed in slot s
    at_slot = [[f"piece_{i}_in_slot_{s}" for s in range(n_pieces)] for i in range(n_pieces)]
    for i in range(n_pieces):
        for s in range(n_pieces):
            solver.addVariable(at_slot[i][s], 0, 1)
    # each piece is rehearsed exactly once
    for i in range(n_pieces):
        solver.addConstraint([(1, at_slot[i][s]) for s in range(n_pieces)], True, 1, True, 1)
    # each slot rehearses exactly one piece
    for s in range(n_pieces):
        solver.addConstraint([(1, at_slot[i][s]) for i in range(n_pieces)], True, 1, True, 1)

    # rehearsal_order[s] is the piece rehearsed in slot s, the i whose at_slot[i][s] is 1
    rehearsal_order = [f"rehearsal_order_{s}" for s in range(n_pieces)]
    for s in range(n_pieces):
        solver.addVariable(rehearsal_order[s], 0, n_pieces - 1)
        solver.addConstraint([(i, at_slot[i][s]) for i in range(1, n_pieces)] + [(-1, rehearsal_order[s])],
                             True, 0, True, 0)

    # slot_of[i] is the slot in which piece i is rehearsed
    slot_of = [f"slot_of_{i}" for i in range(n_pieces)]
    for i in range(n_pieces):
        solver.addVariable(slot_of[i], 0, n_pieces - 1)
        solver.addConstraint([(s, at_slot[i][s]) for s in range(1, n_pieces)] + [(-1, slot_of[i])],
                             True, 0, True, 0)

    # before[i, j] is 1 when piece i is rehearsed before piece j, for i < j. Otherwise j comes first.
    before = {}
    for i in range(n_pieces):
        for j in range(i + 1, n_pieces):
            before[i, j] = f"piece_{i}_before_{j}"
            solver.addVariable(before[i, j], 0, 1)
            solver.addReification(before[i, j], True, [(1, slot_of[j]), (-1, slot_of[i])], 1)

    # start[i] is the time piece i begins: the total duration of the pieces rehearsed before it.
    # A piece j < i comes before i when before[j, i] is 1. A piece j > i comes before i when
    # before[i, j] is 0.
    start = [f"start_{i}" for i in range(n_pieces)]
    for i in range(n_pieces):
        solver.addVariable(start[i], 0, total_time)
        terms = [(1, start[i])]
        terms += [(-duration[j], before[j, i]) for j in range(i)]
        terms += [(duration[j], before[i, j]) for j in range(i + 1, n_pieces)]
        # the total duration of the pieces numbered above i
        total_later = sum(duration[i + 1:])
        solver.addConstraint(terms, True, total_later, True, total_later)

    # arrival[p] is when player p arrives, departure[p] when they leave
    arrival = [f"arrival_{p}" for p in range(n_players)]
    departure = [f"departure_{p}" for p in range(n_players)]
    for p in range(n_players):
        solver.addVariable(arrival[p], 0, total_time)
        solver.addVariable(departure[p], 0, total_time)
        # player p arrives no later than the start of each piece they play in, and leaves no
        # earlier than its end
        for i in range(n_pieces):
            if rehearsal[p][i]:
                solver.addConstraint([(1, start[i]), (-1, arrival[p])], True, 0)
                solver.addConstraint([(1, departure[p]), (-1, start[i])], True, duration[i])

    # The total waiting time: the time each player is present, summed over the players who play
    # in some piece, less the time they spend playing, which the data fixes.
    playing_time = sum(duration[i] for p in range(n_players) for i in range(n_pieces) if rehearsal[p][i])
    objective = []
    for p in range(n_players):
        if any(rehearsal[p]):
            objective.append((1, departure[p]))
            objective.append((-1, arrival[p]))

    solver.setObjective(objective, minimize=True, offset=-playing_time)

    return solver, {"rehearsal_order": rehearsal_order}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
