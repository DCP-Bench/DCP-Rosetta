# big_bang2: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python big_bang2.py

from pyscipopt import Model, quicksum


def create_model(instance):
    """Five nontransitive dice, one per choice of Rock, Paper, Scissors, Lizard and
    Spock. Each die has six faces, each a whole number from 1 to 12, and faces may
    repeat. Die A beats die B when A's face is strictly larger than B's face in more
    than half of the 36 pairs of faces. The ten beats of the game must hold between
    the dice; the dice are numbered 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock.

    The instance file is empty ([]): the statement fixes every size and value, so
    the instance argument is not read.
    """
    n_dice = 5   # five dice, one per choice of the game (statement)
    n_faces = 6  # six faces per die (statement)

    # The ten beats of the statement as (winner, loser) die numbers.
    beats = [(0, 2), (0, 3), (1, 0), (1, 4), (2, 1),
             (2, 3), (3, 1), (3, 4), (4, 0), (4, 2)]

    # More than half of the 36 face pairs (6 x 6) is at least 19 pairs.
    needed = n_faces * n_faces // 2 + 1

    model = Model("big_bang2")

    # dice[d, f] is the value of face f of die d. The range 1 to 12 is from the statement.
    dice = model.addMatrixVar((n_dice, n_faces), vtype="I", lb=1, ub=12, name="dice")

    # larger[k, p, q] is 1 when face p of the winner of beat k is larger than face q of
    # its loser. SCIP has no strict >, so "larger" is written as a difference of at
    # least 1, which is exact for integers.
    larger = model.addMatrixVar((len(beats), n_faces, n_faces), vtype="B", name="larger")

    for k, (winner, loser) in enumerate(beats):
        for p in range(n_faces):
            for q in range(n_faces):
                # Only this direction is posted: a 1 forces the difference. The count
                # below needs at least 19 ones, so every counted pair really is larger.
                model.addConsIndicator(
                    dice[winner, p] - dice[loser, q] >= 1, binvar=larger[k, p, q])

        # The winner beats the loser: more than half of the 36 face pairs are won by its face.
        model.addCons(
            quicksum(larger[k, p, q] for p in range(n_faces) for q in range(n_faces))
            >= needed)

    return model, {"dice": dice}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
