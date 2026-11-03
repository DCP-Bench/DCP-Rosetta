# big_bang2: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python big_bang2.py

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Design five six-sided dice, one for each of Rock, Paper, Scissors, Lizard and Spock,
    so that each die beats exactly the two dice that its choice beats in the game. Die A beats
    die B when A shows a strictly larger value than B in more than half of all pairs of faces."""
    # The five choices, numbered 0 to 4 in the order of the dice.
    rock, paper, scissors, lizard, spock = range(5)
    n_dice = 5      # one die per choice
    n_faces = 6     # each die has six faces
    max_face = 12   # each face shows a value from 1 to max_face, both included

    # (winner, loser): the ten 'beats' relationships of the game
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

    pool = IDPool()

    # dice[d][f] is the value on face f of die d; values may repeat within a die and across dice.
    dice = [[Integer(f"dice{d}_{f}", 1, max_face, encoding="coupled", vpool=pool)
             for f in range(n_faces)] for d in range(n_dice)]
    engine = IntegerEngine(vars=[face for die in dice for face in die], vpool=pool)
    formula = engine.clausify()

    # For each 'beats' relationship, the winner has to win more than half of the pairs of faces.
    for winner, loser in beats:
        pairs_won = []
        for x in range(n_faces):
            for y in range(n_faces):
                a, b = dice[winner][x], dice[loser][y]
                # won[x, y] is true when face x of the winner is larger than face y of the loser.
                won = pool.id(("wins", winner, loser, x, y))
                # Forcing won true requires the winner's face to be larger: at least 2, and above
                # every value the loser's face can reach below it, up to max_face.
                formula.append([-won, a.ge(2)])
                for v in range(2, max_face):
                    formula.append([-won, -b.ge(v), a.ge(v + 1)])
                formula.append([-won, -b.ge(max_face)])
                pairs_won.append(won)
        # More than half of the n_faces * n_faces pairs of faces are won.
        formula.extend(CardEnc.atleast(lits=pairs_won, bound=(n_faces * n_faces) // 2 + 1,
                                       vpool=pool, encoding=EncType.seqcounter).clauses)

    return formula, {"dice": dice}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
