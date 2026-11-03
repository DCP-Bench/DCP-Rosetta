# big_bang2: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Run it (after `pip install mip numpy`) with:
#   python big_bang2.py

import mip


def create_model(instance):
    """Five six-sided dice, one each for Rock, Paper, Scissors, Lizard and Spock, with face
    values from 1 to 12. Each die beats the two dice that its choice beats in the game. A die
    beats another when it shows a strictly larger value on more than half of the pairs of faces."""
    n_dice = 5                                  # one die for each choice
    rock, paper, scissors, lizard, spock = range(n_dice)
    n_faces = 6                                 # faces on each die
    max_face = 12                               # largest face value
    n_pairs = n_faces * n_faces                 # pairs of faces of two dice
    min_pairs_won = n_pairs // 2 + 1            # more than half of the pairs

    # (winner, loser): the ten beats relations of the game
    beats = [
        (rock, scissors),      # rock crushes scissors
        (rock, lizard),        # rock crushes lizard
        (paper, rock),         # paper covers rock
        (paper, spock),        # paper disproves Spock
        (scissors, paper),     # scissors cut paper
        (scissors, lizard),    # scissors decapitate lizard
        (lizard, paper),       # lizard eats paper
        (lizard, spock),       # lizard poisons Spock
        (spock, rock),         # Spock vaporizes rock
        (spock, scissors),     # Spock smashes scissors
    ]

    model = mip.Model(solver_name="CBC")

    # at_least[d, f, t] is 1 when face f of die d shows at least t, for t from 2 to max_face
    at_least = {}
    for d in range(n_dice):
        for f in range(n_faces):
            for t in range(2, max_face + 1):
                at_least[d, f, t] = model.add_var(f"at_least_{d}_{f}_{t}", var_type=mip.BINARY)

    # The value of face f of die d: 1 plus the number of thresholds from 2 up to it that it reaches.
    def face_value(d, f):
        return 1 + mip.xsum(at_least[d, f, t] for t in range(2, max_face + 1))

    # A face that shows at least t + 1 also shows at least t.
    for d in range(n_dice):
        for f in range(n_faces):
            for t in range(2, max_face):
                model.add_constr(at_least[d, f, t + 1] <= at_least[d, f, t])

    # One flag per pair of faces, for each beats relation. The flag is 1 only when the winner's
    # face is strictly larger than the loser's face. At least min_pairs_won flags are 1.
    for r, (winner, loser) in enumerate(beats):
        wins = []
        for a in range(n_faces):
            for b in range(n_faces):
                win = model.add_var(f"win_{r}_{a}_{b}", var_type=mip.BINARY)
                wins.append(win)
                # If the flag is 1 and the loser's face shows at least t, the winner's face shows at
                # least t + 1. Every threshold t from 1 to max_face is checked.
                for t in range(1, max_face + 1):
                    terms = [(win, 1)]
                    const = 0
                    if t == 1:
                        const += 1  # every face shows at least 1
                    else:
                        terms.append((at_least[loser, b, t], 1))
                    if t < max_face:
                        terms.append((at_least[winner, a, t + 1], -1))
                    model.add_constr(mip.xsum(c * v for v, c in terms) <= 1 - const)
        model.add_constr(mip.xsum(wins) >= min_pairs_won)

    # dice[d][f]: the value on face f of die d, rows in the order Rock, Paper, Scissors, Lizard, Spock
    dice = [[face_value(d, f) for f in range(n_faces)] for d in range(n_dice)]

    return model, {"dice": dice}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
