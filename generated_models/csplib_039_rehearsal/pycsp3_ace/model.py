# csplib_039_rehearsal: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_039_rehearsal.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_039_rehearsal.py csplib_039_rehearsal.json

from pycsp3 import *


def create_model(instance):
    """A concert consists of pieces of music of different durations, each involving a different
    combination of the members of the orchestra. Players arrive at rehearsals immediately before the
    first piece in which they are involved and depart immediately after the last. Devise an order in
    which the pieces can be rehearsed so as to minimise the total time that players are waiting to
    play, i.e. the total time when players are present but not currently playing."""
    n_pieces = instance["num_pieces"]     # the number of pieces
    n_players = instance["num_players"]   # the number of players
    duration = instance["duration"]       # duration[j] is the length of piece j
    rehearsal = instance["rehearsal"]     # rehearsal[p][j] is 1 when player p is involved in piece j

    # order[i] is the piece rehearsed in slot i
    order = VarArray(size=n_pieces, dom=range(n_pieces))
    # slot_duration[i] is the length of the piece rehearsed in slot i
    slot_duration = VarArray(size=n_pieces, dom=sorted(set(duration)))
    # plays[p][i] is 1 when player p is involved in the piece rehearsed in slot i
    plays = VarArray(size=[n_players, n_pieces], dom={0, 1})
    # present[p][i] is 1 when player p is at the rehearsal in slot i: after his first piece and before his last
    present = VarArray(size=[n_players, n_pieces], dom={0, 1})

    satisfy(
        # Each piece is rehearsed in exactly one slot.
        AllDifferent(order),
        # The slot duration is the length of the piece rehearsed in that slot.
        [
            Table(scope=[order[i], slot_duration[i]], supports=[(j, duration[j]) for j in range(n_pieces)])
            for i in range(n_pieces)
        ],
        # Whether a player is involved in the piece rehearsed in each slot.
        [
            Table(scope=[order[i], plays[p][i]], supports=[(j, rehearsal[p][j]) for j in range(n_pieces)])
            for p in range(n_players)
            for i in range(n_pieces)
        ],
        # A player is present in slot i when he plays in some slot up to i and in some slot from i on.
        [
            (present[p][i] == 1)
            == And(
                Sum(plays[p][k] for k in range(i + 1)) >= 1,
                Sum(plays[p][k] for k in range(i, n_pieces)) >= 1,
            )
            for p in range(n_players)
            for i in range(n_pieces)
        ],
    )

    # The time players are present but not playing: the time present, minus the time each player spends
    # playing (the total length of the pieces he is involved in, which does not depend on the order).
    playing_time = sum(duration[j] * rehearsal[p][j] for p in range(n_players) for j in range(n_pieces))
    minimize(
        Sum(slot_duration[i] * present[p][i] for p in range(n_players) for i in range(n_pieces)) - playing_time
    )

    return {"rehearsal_order": order}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
