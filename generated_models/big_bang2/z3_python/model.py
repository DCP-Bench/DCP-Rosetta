# big_bang2: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Run it (after `pip install z3-solver numpy`) with:
#   python big_bang2.py

import z3


def create_model(instance):
    """Design five six-sided dice, one for each of Rock, Paper, Scissors, Lizard and Spock,
    so that each die beats exactly the two dice its choice beats in the game. Die A beats
    die B when A shows a strictly larger value than B on more than half of all pairs of faces."""
    # The five choices, numbered as the rows of dice
    rock, paper, scissors, lizard, spock = choices = range(5)
    n_faces = 6    # each die has six faces
    max_face = 12  # face values go from 1 to 12

    # (winner, loser): the ten beats relationships of the game
    beats = [
        (rock, scissors),     # rock crushes scissors
        (rock, lizard),       # rock crushes lizard
        (paper, rock),        # paper covers rock
        (paper, spock),       # paper disproves Spock
        (scissors, paper),    # scissors cuts paper
        (scissors, lizard),   # scissors decapitate lizard
        (lizard, paper),      # lizard eats paper
        (lizard, spock),      # lizard poisons Spock
        (spock, rock),        # Spock vaporizes rock
        (spock, scissors),    # Spock smashes scissors
    ]

    # dice[c][f] is the value on face f of the die for choice c; values may repeat within a die and across dice
    dice = [[z3.Int(f"dice_{c}_{f}") for f in range(n_faces)] for c in choices]

    solver = z3.Solver()

    # Every face shows a value from 1 to max_face.
    solver.add([z3.And(1 <= face, face <= max_face) for die in dice for face in die])

    # Each beats relationship holds between its two dice.
    for winner, loser in beats:
        # n_pairs_won: the number of pairs of faces where the winner's face is the larger one
        n_pairs_won = z3.Sum([z3.If(a > b, 1, 0) for a in dice[winner] for b in dice[loser]])
        solver.add(n_pairs_won > n_faces * n_faces // 2)

    return solver, {"dice": dice}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
