# session1_thick_as_thieves: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python session1_thick_as_thieves.py

from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool

# The six suspects.
SUSPECTS = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]


def create_model(instance):
    """Six suspects were interviewed about a robbery. The innocent tell the truth and the
    guilty lie about what they said. Who is guilty?"""
    pool = IDPool()  # hands out the variable numbers

    # guilty[name] is true when that suspect took part in the robbery.
    guilty = {name: pool.id(name) for name in SUSPECTS}
    artie, bill, crackitt, dodgy, edgy, fingers = (guilty[name] for name in SUSPECTS)

    cnf = CNF()

    # The getaway car barely held two, so at most two suspects are guilty.
    cnf.extend(CardEnc.atmost(lits=list(guilty.values()), bound=2, vpool=pool,
                              encoding=EncType.seqcounter).clauses)

    # Each suspect is guilty exactly when what they said is false.

    # Artie ("It wasn't me.") and Crackitt ("No I wasn't.") deny their own guilt. Either
    # way the statement agrees with the rule, so these two statements decide nothing.

    # Bill: "Crackitt was in it up to his neck." Bill is guilty exactly when Crackitt is not.
    cnf.append([bill, crackitt])
    cnf.append([-bill, -crackitt])

    # Dodgy: "If Crackitt did it, Bill did it with him." The statement is false exactly when
    # Crackitt is guilty and Bill is not, and then Dodgy is guilty.
    cnf.append([-dodgy, crackitt])
    cnf.append([-dodgy, -bill])
    cnf.append([dodgy, -crackitt, bill])

    # Edgy: "Nobody did it alone." The statement is false exactly when at most one suspect
    # is guilty, so Edgy is guilty exactly then.
    # If Edgy is guilty, at most one suspect is guilty.
    for a, b in combinations(guilty.values(), 2):
        cnf.append([-edgy, -a, -b])
    # If Edgy is innocent, at least two suspects are guilty: no single suspect is the only
    # guilty one.
    for name in SUSPECTS:
        cnf.append([edgy] + [guilty[other] for other in SUSPECTS if other != name])

    # Fingers: "That's right: it was Artie and Dodgy together." Fingers is guilty exactly
    # when Artie and Dodgy are not both guilty.
    cnf.append([-fingers, -artie, -dodgy])
    cnf.append([fingers, artie])
    cnf.append([fingers, dodgy])

    return cnf, guilty


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
