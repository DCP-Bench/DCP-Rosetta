# big_bang2: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python big_bang2.py

from docplex.mp.model import Model


def create_model(instance):
    """Nontransitive dice for Rock-Paper-Scissors-Lizard-Spock: five six-faced dice with faces 1..12
    whose "beats" relation (a die beats another when its face is strictly larger in more than half of
    the 36 face pairs) matches the ten "beats" relations of the game."""
    rock, paper, scissors, lizard, spock = range(5)
    n_dice = 5     # number of dice (puzzle constant)
    n_faces = 6    # faces per die (puzzle constant)
    max_face = 12  # largest face value (puzzle constant)
    # Who beats whom in the game, as [winner, loser] (puzzle constant).
    beats = [
        [rock, scissors],     # Rock crushes Scissors
        [rock, lizard],       # Rock crushes Lizard
        [paper, rock],        # Paper covers Rock
        [paper, spock],       # Paper disproves Spock
        [scissors, paper],    # Scissors cuts Paper
        [scissors, lizard],   # Scissors decapitates Lizard
        [lizard, paper],      # Lizard eats Paper
        [lizard, spock],      # Lizard poisons Spock
        [spock, rock],        # Spock vaporizes Rock
        [spock, scissors],    # Spock smashes Scissors
    ]
    faces = range(n_faces)

    model = Model("big_bang2")

    # dice[i][j] is the value of face j of die i (Rock = 0, Paper = 1, Scissors = 2, Lizard = 3,
    # Spock = 4); faces may repeat within and across dice.
    dice = [[model.integer_var(1, max_face, name=f"dice_{i}_{j}") for j in faces] for i in range(n_dice)]

    # A winner beats a loser when its face is strictly larger than the loser's face in more than half
    # of the pairs of faces. A binary may be 1 only for a pair where the winner's face x is larger
    # than the loser's face y, and more than half of the pairs must have it at 1.
    for winner, loser in beats:
        larger = []
        for x in faces:
            for y in faces:
                is_larger = model.binary_var(name=f"wins_{winner}_{loser}_{x}_{y}")
                model.add_indicator(is_larger, dice[winner][x] >= dice[loser][y] + 1)
                larger.append(is_larger)
        model.add_constraint(model.sum(larger) >= n_faces * n_faces // 2 + 1)

    return model, {"dice": dice}


if __name__ == "__main__":
    model, outputs = create_model({})
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
