# who_killed_agatha: a PySAT (Python) model from DCP Rosetta.
# Download the `who_killed_agatha.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python who_killed_agatha.py who_killed_agatha.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Agatha, the butler and Charles live in Dreadsbury Mansion, and one of them killed
    Aunt Agatha. A killer hates his victim and is no richer than his victim. The clues say
    who hates whom and who is richer than whom. Find the killer."""
    n = len(instance["names"])  # the number of people in the mansion
    agatha, butler, charles = 0, 1, 2  # the places of Agatha, the butler and Charles among the people
    victim = agatha  # the person who was killed

    pool = IDPool()  # gives each fact below its own variable

    # the killer, one of the people in the mansion
    killer = Integer("killer", 0, n - 1, vpool=pool)
    engine = IntegerEngine(vars=[killer], vpool=pool)
    cnf = engine.clausify()  # the constraints on the killer

    # hates[i][j] is true when person i hates person j
    hates = [[pool.id(("hates", i, j)) for j in range(n)] for i in range(n)]
    # richer[i][j] is true when person i is richer than person j
    richer = [[pool.id(("richer", i, j)) for j in range(n)] for i in range(n)]

    # A killer always hates, and is no richer than, his victim.
    for person in range(n):
        cnf.append([-killer.equals(person), hates[person][victim]])
        cnf.append([-killer.equals(person), -richer[person][victim]])

    # Nobody is richer than himself, and of two different people exactly one is richer.
    for i in range(n):
        cnf.append([-richer[i][i]])
        for j in range(i + 1, n):
            cnf.append([richer[i][j], richer[j][i]])
            cnf.append([-richer[i][j], -richer[j][i]])

    # Charles hates nobody that Agatha hates.
    for i in range(n):
        cnf.append([-hates[agatha][i], -hates[charles][i]])

    # Agatha hates everybody except the butler.
    for i in range(n):
        cnf.append([-hates[agatha][i] if i == butler else hates[agatha][i]])

    # The butler hates everyone not richer than Aunt Agatha.
    for i in range(n):
        cnf.append([richer[i][agatha], hates[butler][i]])

    # The butler hates everyone whom Agatha hates.
    for i in range(n):
        cnf.append([-hates[agatha][i], hates[butler][i]])

    # Nobody hates everyone: each person hates at most n - 1 people.
    for i in range(n):
        cnf.extend(CardEnc.atmost(lits=hates[i], bound=n - 1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    return cnf, {"killer": killer}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
