# fifty_puzzle: a PySAT (Python) model from DCP Rosetta.
# Download the `fifty_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python fifty_puzzle.py fifty_puzzle.json

from pysat.formula import CNF, IDPool
from pysat.pb import PBEnc


def create_model(instance):
    """Dummies numbered with integers are to be knocked over with baseballs: choose
    the dummies to knock down so that their numbers add up to exactly the target sum,
    neither more nor less."""
    values = instance["values"]          # values[i]: the number on dummy i
    target_sum = instance["target_sum"]  # the sum the knocked-over numbers must reach

    pool = IDPool()
    # dummies[i] is true when dummy i is knocked over
    dummies = [pool.id(("d", i)) for i in range(len(values))]

    cnf = CNF()
    # The numbers on the knocked-over dummies add up to exactly the target sum.
    cnf.extend(PBEnc.equals(lits=dummies, weights=list(values), bound=target_sum,
                            vpool=pool).clauses)

    return cnf, {"dummies": dummies}


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
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
