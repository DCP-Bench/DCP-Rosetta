# csplib_039_rehearsal: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_039_rehearsal.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_039_rehearsal.py csplib_039_rehearsal.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """A concert consists of pieces of different durations, each played by a different combination
    of orchestra members. A player arrives just before the first piece they play in and leaves
    just after the last. Order the pieces for rehearsal so that the total time players spend
    present but not playing is as small as possible."""
    n_pieces = instance["num_pieces"]          # the number of pieces, which is also the number of slots
    n_players = instance["num_players"]        # the number of players
    duration = instance["duration"]            # duration[j]: the length of piece j
    rehearsal = instance["rehearsal"]          # rehearsal[p][j] is 1 when player p plays in piece j
    slots = range(n_pieces)

    pool = IDPool()
    # rehearsal_order[i] is the piece rehearsed in slot i, numbered from 0
    rehearsal_order = [Integer(f"rehearsal_order{i}", 0, max(n_pieces - 1, 1), vpool=pool)
                       for i in slots]
    # is_piece[i][j] is true when slot i holds piece j
    is_piece = [[rehearsal_order[i].equals(j) for j in range(n_pieces)] for i in slots]

    formula = WCNF()
    formula.extend(IntegerEngine(vars=rehearsal_order, vpool=pool).clausify().clauses)
    # With a single piece, the only slot holds piece 0.
    if n_pieces == 1:
        formula.append([-rehearsal_order[0].equals(1)])

    # Each piece is rehearsed in exactly one slot, so the order is a permutation of the pieces.
    for j in range(n_pieces):
        formula.extend(CardEnc.equals(lits=[is_piece[i][j] for i in slots], bound=1,
                                      vpool=pool, encoding=EncType.seqcounter).clauses)

    for p in range(n_players):
        mine = [j for j in range(n_pieces) if rehearsal[p][j] == 1]  # the pieces player p plays in
        # plays[i] is true when player p plays in the piece of slot i
        plays = [pool.id(("plays", p, i)) for i in slots]
        for i in slots:
            for j in mine:
                formula.append([-is_piece[i][j], plays[i]])

        # arrived[i]: player p has arrived by slot i. not_departed[i]: player p has not left by
        # slot i. Presence costs time, so an optimal order keeps both as small as the plays allow.
        arrived = [pool.id(("arrived", p, i)) for i in slots]
        not_departed = [pool.id(("still", p, i)) for i in slots]
        # A player who plays in slot i has arrived and has not left by then. Arriving is kept
        # from one slot to the next, and so is not leaving, read backwards.
        for i in slots:
            formula.append([-plays[i], arrived[i]])
            formula.append([-plays[i], not_departed[i]])
            if i > 0:
                formula.append([-arrived[i - 1], arrived[i]])
            if i + 1 < n_pieces:
                formula.append([-not_departed[i + 1], not_departed[i]])

        # Waiting time: player p is present in slot i (arrived, not yet left) while the piece in
        # that slot is one they do not play. That costs the piece's duration.
        for i in slots:
            for j in range(n_pieces):
                if rehearsal[p][j] == 0 and duration[j] > 0:
                    formula.append([-arrived[i], -not_departed[i], -is_piece[i][j]],
                                   weight=duration[j])

    return formula, {"rehearsal_order": rehearsal_order}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
