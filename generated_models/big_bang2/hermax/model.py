# big_bang2: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Run it (after `pip install hermax`) with:
#   python big_bang2.py

from hermax.model import Model

# The game is fixed by the problem: five choices, and ten "beats" relations between them.
# Rock(0), Paper(1), Scissors(2), Lizard(3), Spock(4) are the row indices of the dice.
ROCK, PAPER, SCISSORS, LIZARD, SPOCK = range(5)
BEATS = [
    (ROCK, SCISSORS),      # Rock crushes Scissors
    (ROCK, LIZARD),        # Rock crushes Lizard
    (PAPER, ROCK),         # Paper covers Rock
    (PAPER, SPOCK),        # Paper disproves Spock
    (SCISSORS, PAPER),     # Scissors cuts Paper
    (SCISSORS, LIZARD),    # Scissors decapitate Lizard
    (LIZARD, PAPER),       # Lizard eats Paper
    (LIZARD, SPOCK),       # Lizard poisons Spock
    (SPOCK, ROCK),         # Spock vaporizes Rock
    (SPOCK, SCISSORS),     # Spock smashes Scissors
]


def create_model(instance):
    """Nontransitive dice: find five six-faced dice, each face a value from 1 to 12 (repeats
    allowed), such that die A beats die B exactly when the game's relation says so. A beats B
    when A shows a strictly larger face than B in more than half of the 36 pairs of faces.

    The instance carries no data: the game and the face values are all fixed by the statement."""
    dice_count = 5   # one die per choice, row 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock
    faces = 6        # faces per die
    top = 12         # the largest face value; faces take values 1..top

    m = Model()

    # dice[i][j] is the value on face j of die i
    dice = m.int_matrix("dice", dice_count, faces, 1, top)

    # Each of the ten beats relations: the winner shows the larger face in more than half of
    # the 36 pairs of faces, i.e. in at least 19 of them.
    for winner, loser in BEATS:
        # pairs[x][y] is true when face x of the winner is larger than face y of the loser
        pairs = m.bool_matrix(f"larger_{winner}_{loser}", faces, faces)
        for x in range(faces):
            for y in range(faces):
                m &= (dice[winner][x] > dice[loser][y]).iff(pairs[x][y])
        # the winner's faces are larger than the loser's in more than half of the pairs
        m &= (sum(pairs.flatten()) >= faces * faces // 2 + 1)

    # Satisfaction problem: no objective.
    return m, {"dice": dice}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
