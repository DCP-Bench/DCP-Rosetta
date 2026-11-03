# big_bang2: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Run it (after `pip install cpmpy`) with:
#   python big_bang2.py

import cpmpy as cp


def create_model(instance):
    """Design five six-sided dice, one for each of Rock, Paper, Scissors, Lizard and Spock,
    so that each die beats exactly the two dice that its choice beats in the game. Die A beats
    die B when A shows a strictly larger value than B in more than half of all pairs of faces."""
    # The problem statement fixes all the data.
    rock, paper, scissors, lizard, spock = range(5)
    n_faces = 6      # each die has six faces
    max_face = 12    # face values go from 1 to 12

    # (winner, loser): the ten 'beats' relationships of the game
    beats = [
        (rock, scissors),      # rock crushes scissors
        (rock, lizard),        # rock crushes lizard
        (paper, rock),         # paper covers rock
        (paper, spock),        # paper disproves Spock
        (scissors, paper),     # scissors cuts paper
        (scissors, lizard),    # scissors decapitates lizard
        (lizard, paper),       # lizard eats paper
        (lizard, spock),       # lizard poisons Spock
        (spock, rock),         # Spock vaporizes rock
        (spock, scissors),     # Spock smashes scissors
    ]

    # dice[d, f] is the value on face f of die d (row 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock);
    # face values may repeat within a die and across dice
    dice = cp.intvar(1, max_face, shape=(5, n_faces), name="dice")

    model = cp.Model()
    # The winning die beats the losing die: in more than half of the n_faces * n_faces pairs of
    # faces, the winner shows the strictly larger value.
    for winner, loser in beats:
        pairs_won = [a > b for a in dice[winner] for b in dice[loser]]
        model.add(cp.sum(pairs_won) > (n_faces * n_faces) // 2)

    return model, {"dice": dice}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
