# big_bang2: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Run it (after `pip install pulp numpy`) with:
#   python big_bang2.py

import pulp


def create_model(instance):
    """Nontransitive dice: five six-sided dice, one for each of Rock, Paper, Scissors, Lizard
    and Spock, with faces from 1 to 12, so that each of the ten 'beats' relations of the game
    holds. Die A beats die B when A shows a strictly larger face in more than half of the 36
    pairs of faces, one face from each die."""
    # The five choices, one die for each.
    rock, paper, scissors, lizard, spock = range(5)
    n_dice = 5       # one die for each choice
    n_faces = 6      # each die has six faces
    max_face = 12    # face values run from 1 to 12

    # The ten 'beats' relations, as (winner, loser).
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

    problem = pulp.LpProblem("big_bang2", pulp.LpMinimize)

    # reach[i][j][v] is 1 when face j of die i shows v or more, for v from 2 to max_face
    reach = [[{v: pulp.LpVariable(f"reach_{i}_{j}_{v}", cat="Binary")
               for v in range(2, max_face + 1)}
              for j in range(n_faces)]
             for i in range(n_dice)]

    # Every face shows at least 1, and none shows more than max_face.
    def at_least(i, j, v):
        if v <= 1:
            return 1
        if v > max_face:
            return 0
        return reach[i][j][v]

    # A face that shows v or more also shows v - 1 or more.
    for i in range(n_dice):
        for j in range(n_faces):
            for v in range(3, max_face + 1):
                problem += reach[i][j][v] <= reach[i][j][v - 1]

    # dice[i][j] is the value on face j of die i: 1, plus the values from 2 up that the face shows.
    dice = [[1 + pulp.lpSum(reach[i][j].values()) for j in range(n_faces)]
            for i in range(n_dice)]

    # win[x][y] may be 1 only when face x of the winner is strictly larger than face y of the
    # loser: if the loser's face shows v or more, the winner's face shows v + 1 or more.
    for winner, loser in beats:
        wins = []
        for x in range(n_faces):
            for y in range(n_faces):
                win = pulp.LpVariable(f"win_{winner}_{loser}_{x}_{y}", cat="Binary")
                for v in range(1, max_face + 1):
                    problem += win <= 1 - at_least(loser, y, v) + at_least(winner, x, v + 1)
                wins.append(win)
        # The winner shows the larger face in more than half of the pairs.
        problem += pulp.lpSum(wins) >= (n_faces * n_faces) // 2 + 1

    return problem, {"dice": dice}


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
