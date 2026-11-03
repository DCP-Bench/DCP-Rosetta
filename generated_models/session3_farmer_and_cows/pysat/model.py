# session3_farmer_and_cows: a PySAT (Python) model from DCP Rosetta.
# Download the `session3_farmer_and_cows.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python session3_farmer_and_cows.py session3_farmer_and_cows.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc, EncType as PBEncType


def create_model(instance):
    """A farmer has cows numbered 1 up to the number of cows, and cow i gives i units of
    milk. He gives each son a set number of cows, so that every son gets the same total
    amount of milk. Decide which son gets each cow."""
    num_cows = instance["num_cows"]          # the number of cows, numbered 1..num_cows
    num_sons = instance["num_sons"]          # the number of sons, numbered 0..num_sons-1
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s]: how many cows son s receives

    milk_per_cow = list(range(1, num_cows + 1))   # milk_per_cow[i]: the milk from cow i+1
    milk_per_son = sum(milk_per_cow) // num_sons  # each son's equal share of the milk

    pool = IDPool()

    # cow_assignments[i] is the son who receives cow i+1
    cow_assignments = [Integer(f"cow{i}", 0, num_sons - 1, vpool=pool) for i in range(num_cows)]
    engine = IntegerEngine(vars=cow_assignments, vpool=pool)
    cnf = engine.clausify()

    # gets[s][i] is true when son s receives cow i+1
    gets = [[cow.equals(son) for cow in cow_assignments] for son in range(num_sons)]

    for son in range(num_sons):
        # Son s receives exactly cows_per_son[s] cows.
        cnf.extend(CardEnc.equals(lits=gets[son], bound=cows_per_son[son], vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

        # The milk of the cows son s receives is exactly his equal share.
        cnf.extend(PBEnc.equals(lits=gets[son], weights=milk_per_cow, bound=milk_per_son, vpool=pool,
                                encoding=PBEncType.bdd).clauses)

    # started[s][i] is true only when son s receives one of cows 1..i+1
    started = [[pool.id(("started", son, i)) for i in range(num_cows)] for son in range(num_sons)]
    for son in range(num_sons):
        cnf.append([-started[son][0], gets[son][0]])
        for i in range(1, num_cows):
            cnf.append([-started[son][i], started[son][i - 1], gets[son][i]])

    # Of two neighbouring sons with the same number of cows, the lower-numbered son takes
    # the first cow. The two sons are interchangeable, so this keeps one of their labellings.
    for son in range(num_sons - 1):
        if cows_per_son[son] == cows_per_son[son + 1]:
            cnf.append([-gets[son + 1][0]])
            for i in range(1, num_cows):
                cnf.append([-gets[son + 1][i], started[son][i - 1]])

    return cnf, {"cow_assignments": cow_assignments}


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
