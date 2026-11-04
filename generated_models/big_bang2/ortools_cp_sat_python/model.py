# big_bang2: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Run it (after `pip install ortools`) with:
#   python big_bang2.py

from ortools.sat.python import cp_model


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
    BEATS = [
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

    model = cp_model.CpModel()

    # dice[d][f] is the value on face f of die d
    dice = [[model.new_int_var(1, max_face, f"dice_{d}_{f}") for f in range(n_faces)]
            for d in range(n_dice)]

    # Each rule: the winning die shows a larger face in more than half of the pairs of faces.
    for winner, loser in BEATS:
        # one flag per pair of faces: true when the winner's face is larger
        wins = []
        for a in dice[winner]:
            for b in dice[loser]:
                larger = model.new_bool_var(f"larger_{winner}_{loser}_{len(wins)}")
                model.add(a > b).only_enforce_if(larger)
                model.add(a <= b).only_enforce_if(~larger)
                wins.append(larger)
        model.add(sum(wins) > n_faces * n_faces // 2)

    # Any dice that follow the rules are an answer.
    return model, {"dice": dice}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
