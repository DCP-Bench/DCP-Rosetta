# big_bang2: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python big_bang2.py

from pycsp3 import *


def create_model(instance):
    """Five nontransitive dice, each with six faces showing a value from 1 to 12,
    so that the dice beat each other in the pattern of Rock, Paper, Scissors,
    Lizard and Spock. A die beats another when its faces are larger than the
    other die's faces in more than half of all pairs of faces."""
    n_dice = 5                       # one die per choice: Rock, Paper, Scissors, Lizard, Spock
    n_faces = 6                      # faces on each die
    lowest_face = 1                  # face values run from 1 to 12 inclusive
    highest_face = 12
    ROCK, PAPER, SCISSORS, LIZARD, SPOCK = range(n_dice)

    # beats[d] lists the dice that die d beats, as stated by the problem:
    # Rock crushes Scissors and Lizard, Paper covers Rock and disproves Spock,
    # Scissors cuts Paper and decapitates Lizard, Lizard eats Paper and poisons Spock,
    # Spock vaporizes Rock and smashes Scissors.
    beats = {
        ROCK: [SCISSORS, LIZARD],
        PAPER: [ROCK, SPOCK],
        SCISSORS: [PAPER, LIZARD],
        LIZARD: [PAPER, SPOCK],
        SPOCK: [ROCK, SCISSORS],
    }

    # dice[d][f] is the value on face f of die d.
    dice = VarArray(size=[n_dice, n_faces], dom=range(lowest_face, highest_face + 1))

    min_wins = n_faces * n_faces // 2 + 1  # more than half of all pairs of faces

    for winner, losers in beats.items():
        for loser in losers:
            # Each die beats the dice listed for it: it has the larger face in more than half of
            # all pairs of faces.
            satisfy(
                Sum(dice[winner][i] > dice[loser][j] for i in range(n_faces) for j in range(n_faces))
                >= min_wins
            )

    return {"dice": dice}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        print("dice", "=")
        for row in outputs["dice"]:
            print(values(row))
    else:
        print("No solution:", status())
