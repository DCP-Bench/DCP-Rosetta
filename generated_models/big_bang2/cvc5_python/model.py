# big_bang2: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Run it (after `pip install cvc5 numpy`) with:
#   python big_bang2.py

import cvc5.pythonic as c5


def create_model(instance):
    """Design five six-sided dice, one for each of Rock, Paper, Scissors, Lizard and Spock,
    so that each die beats exactly the two dice that its choice beats in the game. A die
    beats another when it shows a strictly larger value in more than half of all pairs of
    faces."""
    # The five choices, one die each.
    rock, paper, scissors, lizard, spock = range(5)
    n_dice = 5       # one die per choice
    n_faces = 6      # each die has six faces
    max_face = 12    # face values go from 1 to 12, and may repeat
    min_wins = n_faces * n_faces // 2 + 1  # more than half of the 36 pairs of faces

    # (winner, loser): the ten beats relationships of the game
    beats = [
        (rock, scissors),   # rock crushes scissors
        (rock, lizard),     # rock crushes lizard
        (paper, rock),      # paper covers rock
        (paper, spock),     # paper disproves Spock
        (scissors, paper),  # scissors cuts paper
        (scissors, lizard), # scissors decapitate lizard
        (lizard, paper),    # lizard eats paper
        (lizard, spock),    # lizard poisons Spock
        (spock, rock),      # Spock vaporizes rock
        (spock, scissors),  # Spock smashes scissors
    ]

    # shows[d][f][v]: face f of die d shows v or more, for v from 2 to 12
    shows = [
        [{v: c5.Bool(f"shows_{d}_{f}_{v}") for v in range(2, max_face + 1)} for f in range(n_faces)]
        for d in range(n_dice)
    ]

    # Linear integer logic: cvc5 solves this model much faster than with the default Solver().
    solver = c5.SolverFor("QF_LIA")

    # A face that shows v + 1 or more also shows v or more.
    for d in range(n_dice):
        for f in range(n_faces):
            for v in range(2, max_face):
                solver.add(c5.Implies(shows[d][f][v + 1], shows[d][f][v]))

    def face_value(d, f):
        # A face shows 1 plus the number of thresholds it reaches, so it stays from 1 to 12.
        return 1 + c5.Sum([c5.If(shows[d][f][v], 1, 0) for v in range(2, max_face + 1)])

    def pair_wins(a_die, a_face, b_die, b_face):
        # The pair counts as a win only when face a is strictly larger: some threshold that
        # a reaches and b does not.
        win = c5.Bool(f"win_{a_die}_{a_face}_{b_die}_{b_face}")
        solver.add(c5.Implies(win, c5.Or([
            c5.And(shows[a_die][a_face][v], c5.Not(shows[b_die][b_face][v]))
            for v in range(2, max_face + 1)
        ])))
        return win

    def at_least(flags, k, name):
        # seen[j]: at least j of the flags read so far are true, for j from 1 to k
        seen = {j: c5.Bool(f"{name}_0_{j}") for j in range(1, k + 1)}
        solver.add([c5.Not(seen[j]) for j in range(1, k + 1)])
        for step, flag in enumerate(flags, start=1):
            now = {j: c5.Bool(f"{name}_{step}_{j}") for j in range(1, k + 1)}
            solver.add(c5.Implies(now[1], c5.Or(seen[1], flag)))
            for j in range(2, k + 1):
                solver.add(c5.Implies(now[j], c5.Or(seen[j], c5.And(seen[j - 1], flag))))
            seen = now
        solver.add(seen[k])

    # The winning die shows a larger value on more than half of the pairs of faces.
    for winner, loser in beats:
        wins = [pair_wins(winner, fa, loser, fb) for fa in range(n_faces) for fb in range(n_faces)]
        at_least(wins, min_wins, f"count_{winner}_{loser}")

    # the value on each face of each die
    return solver, {"dice": [[face_value(d, f) for f in range(n_faces)] for d in range(n_dice)]}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
