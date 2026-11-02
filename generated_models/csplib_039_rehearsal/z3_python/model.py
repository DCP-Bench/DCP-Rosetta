# csplib_039_rehearsal: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_039_rehearsal.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_039_rehearsal.py csplib_039_rehearsal.json

import z3


def create_model(instance):
    """A concert has pieces of different durations, each played by a different group of orchestra
    members. A player arrives just before the first piece they play in and leaves just after the
    last; order the pieces for rehearsal so that the total time players spend present but not
    playing is as small as possible."""
    n_pieces = instance["num_pieces"]    # the number of pieces
    n_players = instance["num_players"]  # the number of players
    duration = instance["duration"]      # duration[q]: the rehearsal time of piece q
    rehearsal = instance["rehearsal"]    # rehearsal[p][q]: whether player p plays in piece q

    # rehearsal_order[i] is the piece rehearsed in slot i
    rehearsal_order = [z3.Int(f"order_{i}") for i in range(n_pieces)]
    # arrival[p] is the first slot in which player p is present, departure[p] the last
    arrival = [z3.Int(f"arrival_{p}") for p in range(n_players)]
    departure = [z3.Int(f"departure_{p}") for p in range(n_players)]

    # The entry of table for the piece in a slot. The piece is a variable, so the entry is picked
    # out by cases.
    def entry_for_piece(piece, table):
        value = table[n_pieces - 1]
        for k in range(n_pieces - 2, -1, -1):
            value = z3.If(piece == k, table[k], value)
        return value

    # the rules the rehearsal must follow
    solver = z3.Optimize()

    # Each slot holds a piece from 0 to n_pieces - 1.
    for piece in rehearsal_order:
        solver.add(z3.And(piece >= 0, piece < n_pieces))

    # Every piece is rehearsed exactly once.
    solver.add(z3.Distinct(rehearsal_order))

    # Arrivals and departures fall within the rehearsal.
    for p in range(n_players):
        solver.add(z3.And(arrival[p] >= 0, arrival[p] <= n_pieces - 1,
                          departure[p] >= 0, departure[p] <= n_pieces - 1))

    # waiting holds the time each player waits in each slot
    waiting = []
    for p in range(n_players):
        for i in range(n_pieces):
            # whether player p plays in the piece rehearsed in slot i
            plays = entry_for_piece(rehearsal_order[i], rehearsal[p]) == 1
            # whether player p is present in slot i
            present = z3.And(arrival[p] <= i, i <= departure[p])
            # A player who plays in a slot is present in it.
            solver.add(z3.Implies(plays, present))
            # A player who is present but not playing waits for the whole piece rehearsed in that slot.
            waiting.append(z3.If(z3.And(present, z3.Not(plays)),
                                 entry_for_piece(rehearsal_order[i], duration), 0))

    # Minimise the total waiting time.
    solver.minimize(z3.Sum(waiting))

    return solver, {"rehearsal_order": rehearsal_order}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
