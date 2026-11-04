# big_bang2: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Run it (after `pip install exact numpy`) with:
#   python big_bang2.py

from exact import Exact


def create_model(instance):
    """Design five six-faced dice, one for each of Rock, Paper, Scissors, Lizard and Spock,
    so that each die beats exactly the two dice that its choice beats in the game. Die A beats
    die B when A shows a strictly larger face than B in more than half of all pairs of faces."""
    rock, paper, scissors, lizard, spock = range(5)  # the five choices; die i belongs to choice i
    n_dice = 5       # one die for each choice
    n_faces = 6      # faces on each die
    max_face = 12    # the largest face value; face values run from 1 to max_face
    big_m = max_face  # the slack that lets a pair of faces that does not count pass
    n_pairs = n_faces * n_faces  # pairs of faces between two dice

    # (winner, loser): the ten beats relations of the game
    beats = [
        (rock, scissors),     # Rock crushes Scissors
        (rock, lizard),       # Rock crushes Lizard
        (paper, rock),        # Paper covers Rock
        (paper, spock),       # Paper disproves Spock
        (scissors, paper),    # Scissors cut Paper
        (scissors, lizard),   # Scissors decapitate Lizard
        (lizard, paper),      # Lizard eats Paper
        (lizard, spock),      # Lizard poisons Spock
        (spock, rock),        # Spock vaporizes Rock
        (spock, scissors),    # Spock smashes Scissors
    ]

    solver = Exact()

    # Exact identifies its variables by name.
    # dice[i][j] is the value on face j of die i. Face values may repeat within a die and across dice.
    dice = [[f"dice_{i}_{j}" for j in range(n_faces)] for i in range(n_dice)]
    for i in range(n_dice):
        for j in range(n_faces):
            solver.addVariable(dice[i][j], 1, max_face)

    # For each beats relation, the winner's die beats the loser's die in more than half of the
    # pairs of faces. A pair counts (wins is 1) only when the winner's face is strictly larger.
    for winner, loser in beats:
        pairs = []  # the pairs of faces that count for the winner
        for x in range(n_faces):
            for y in range(n_faces):
                wins = f"wins_{winner}_{loser}_{x}_{y}"
                solver.addVariable(wins, 0, 1)
                solver.addConstraint([(1, dice[winner][x]), (-1, dice[loser][y]), (-big_m, wins)],
                                     True, 1 - big_m)
                pairs.append((1, wins))
        solver.addConstraint(pairs, True, n_pairs // 2 + 1)

    return solver, {"dice": dice}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
