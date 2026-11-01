# big_bang2: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Run it (after `pip install pychoco numpy`) with:
#   python big_bang2.py

from pychoco.model import Model


def create_model(instance):
    """Nontransitive dice: design five dice with six faces each, one die for each of Rock,
    Paper, Scissors, Lizard and Spock, so that the dice beat each other in the same pattern
    as these choices beat each other. A die beats another when it shows a strictly larger
    face in more than half of all pairs of faces."""
    # The five choices, each with its own die.
    ROCK, PAPER, SCISSORS, LIZARD, SPOCK = range(5)
    n_dice = 5       # one die per choice
    n_faces = 6      # each die has six faces
    max_face = 12    # each face shows a value from 1 to 12; values may repeat

    # (winner, loser): the ten rules of the game. Each choice beats two others.
    beats = [
        (ROCK, SCISSORS),     # rock crushes scissors
        (ROCK, LIZARD),       # rock crushes lizard
        (PAPER, ROCK),        # paper covers rock
        (PAPER, SPOCK),       # paper disproves Spock
        (SCISSORS, PAPER),    # scissors cut paper
        (SCISSORS, LIZARD),   # scissors decapitate lizard
        (LIZARD, PAPER),      # lizard eats paper
        (LIZARD, SPOCK),      # lizard poisons Spock
        (SPOCK, ROCK),        # Spock vaporizes rock
        (SPOCK, SCISSORS),    # Spock smashes scissors
    ]

    model = Model()

    # dice[d][f] is the value on face f of die d
    dice = [[model.intvar(1, max_face, name=f"dice_{d}_{f}") for f in range(n_faces)]
            for d in range(n_dice)]

    # Each rule: the winning die shows a larger face in more than half of the pairs of faces.
    for winner, loser in beats:
        # one flag per pair of faces, true when the winner's face is the larger one
        wins = [model.arithm(dice[winner][a], ">", dice[loser][b]).reify()
                for a in range(n_faces) for b in range(n_faces)]
        model.sum(wins, ">", n_faces * n_faces // 2).post()

    return model, {"dice": dice}, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
