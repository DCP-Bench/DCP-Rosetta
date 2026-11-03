# csplib_039_rehearsal: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_039_rehearsal.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_039_rehearsal.py csplib_039_rehearsal.json

from itertools import combinations

import numpy as np
from pyscipopt import Model, quicksum


def create_model(instance):
    """A concert is a set of pieces of music of different durations, and each piece involves
    a different combination of the orchestra's players. A player arrives just before the
    first piece they are in and leaves just after the last one. Choose the order in which the
    pieces are rehearsed so that the total time players spend waiting (present but not
    playing) is as small as possible."""
    num_pieces = instance["num_pieces"]    # the number of pieces, numbered 0 .. num_pieces - 1
    num_players = instance["num_players"]  # the number of players, numbered 0 .. num_players - 1
    duration = instance["duration"]        # duration[r]: how long piece r takes to rehearse
    rehearsal = instance["rehearsal"]      # rehearsal[j][r] is 1 when player j plays in piece r, and 0 when not
    pieces = range(num_pieces)
    players = range(num_players)

    model = Model("rehearsal")

    # before[p, q] is 1 when piece p is rehearsed before piece q, and 0 when after. A piece is
    # not before itself, so the diagonal is fixed to 0.
    before = model.addMatrixVar((num_pieces, num_pieces), vtype="B", name="before",
                                ub=[[0 if p == q else 1 for q in pieces] for p in pieces])
    # Of two different pieces, exactly one comes first.
    model.addMatrixCons(before + before.T == 1 - np.eye(num_pieces))
    # The pairs form one sequence: no three pieces may go round in a cycle (p before q, q before r,
    # r before p, or the reverse). Each cycle is forbidden by one constraint, one per direction.
    for p, q, r in combinations(pieces, 3):
        model.addCons(before[p, q] + before[q, r] + before[r, p] <= 2)
        model.addCons(before[q, p] + before[r, q] + before[p, r] <= 2)

    # slot[p, s] is 1 when piece p is rehearsed in slot s, the s-th place in the order, counting from 0
    slot = model.addMatrixVar((num_pieces, num_pieces), vtype="B", name="slot")
    # Each piece is in exactly one slot.
    model.addMatrixCons(slot.sum(axis=1) == 1)
    # A piece's slot is the number of pieces rehearsed before it. In a sequence these numbers are
    # 0 .. num_pieces - 1, each used once, so every slot holds exactly one piece.
    model.addMatrixCons(slot @ np.arange(num_pieces) == before.sum(axis=0))

    # wait[j, r] is 1 when player j waits through piece r: player j is not in piece r, but piece r
    # is rehearsed after one of player j's pieces and before another of them. Pieces are rehearsed
    # back to back, so the waiting time of player j is the sum of duration[r] over these pieces.
    wait = {}
    for j in players:
        played = [p for p in pieces if rehearsal[j][p]]
        if not played:
            # A player in no piece is never in the rehearsal room, so they never wait. No
            # variable is created for them.
            continue
        for r in pieces:
            if rehearsal[j][r]:
                continue
            # earlier is 1 when some piece player j is in comes before piece r; later is 1 when
            # some piece player j is in comes after piece r.
            earlier = model.addVar(f"earlier_{j}_{r}", vtype="B")
            later = model.addVar(f"later_{j}_{r}", vtype="B")
            model.addConsOr([before[p, r] for p in played], earlier)
            model.addConsOr([before[r, q] for q in played], later)
            wait[j, r] = model.addVar(f"wait_{j}_{r}", vtype="B")
            model.addConsAnd([earlier, later], wait[j, r])

    # The total waiting time, the sum over players of the durations of the pieces they wait through,
    # is to be minimised.
    model.setObjective(quicksum(duration[r] * var for (j, r), var in wait.items()), "minimize")

    # rehearsal_order[s] is the piece rehearsed in slot s
    rehearsal_order = [quicksum(p * slot[p, s] for p in pieces) for s in pieces]

    return model, {"rehearsal_order": rehearsal_order}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
