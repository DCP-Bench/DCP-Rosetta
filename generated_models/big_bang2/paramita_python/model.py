# big_bang2: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python big_bang2.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Or, add_to_container, to_cnf


def create_model(instance):
    """Design five six-sided dice, one for each of Rock, Paper, Scissors, Lizard and Spock,
    so that each die beats exactly the two dice that its choice beats in the game. Die A beats
    die B when A shows a strictly larger value than B in more than half of all pairs of faces."""
    n_dice = 5                                    # one die for each choice
    rock, paper, scissors, lizard, spock = range(n_dice)
    n_faces = 6                                   # each die has six faces
    max_value = 12                                # face values go from 1 to 12, repeats allowed
    thresholds = range(2, max_value + 1)          # t = 2..12: a face shows at least t
    n_pairs = n_faces * n_faces                   # pairs of faces, one face from each die
    min_wins = n_pairs // 2 + 1                   # more than half of the pairs: 19 of 36

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

    # ge[d][k][t] is true when face k of die d shows at least t
    ge = [[{t: Bool(f"face_{d}_{k}_ge_{t}") for t in thresholds} for k in range(n_faces)]
          for d in range(n_dice)]

    # A face is strictly larger than another when, for some t, it shows at least t and the other shows less.
    def larger(first, second):
        return Or([first[t] & ~second[t] for t in thresholds])

    cons = []   # all constraints on the dice

    # A face that shows at least t also shows at least t - 1.
    for d in range(n_dice):
        for k in range(n_faces):
            for t in range(3, max_value + 1):
                cons.append(If(ge[d][k][t], ge[d][k][t - 1]))

    # The winning die has the larger face in at least min_wins of the pairs of faces.
    for winner, loser in beats:
        wins = []   # one per pair of faces, true only where the winner's face is the larger one
        for i in range(n_faces):
            for j in range(n_faces):
                win = Bool(f"larger_{winner}_{i}_{loser}_{j}")
                cons.append(If(win, larger(ge[winner][i], ge[loser][j])))
                wins.append(win)
        cons.append(sum(wins) >= min_wins)

    # The value on face k of die d is one more than the number of thresholds it reaches.
    dice = [[1 + sum(ge[d][k].values()) for k in range(n_faces)] for d in range(n_dice)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in cons:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"dice": dice}


if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    (formula, pool), outputs = create_model({})

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
