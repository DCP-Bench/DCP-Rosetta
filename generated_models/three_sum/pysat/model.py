# three_sum: a PySAT (Python) model from DCP Rosetta.
# Download the `three_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python three_sum.py three_sum.json

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.pb import PBEnc


def create_model(instance):
    """Given a collection of integers, select exactly m of them so that the selected
    integers sum to zero."""
    nums = instance["nums"]  # nums[i]: the i-th integer of the collection
    m = instance["m"]        # how many integers to select

    pool = IDPool()

    # indices[i] is true when the i-th integer is selected
    indices = [pool.id(("i", i)) for i in range(len(nums))]

    cnf = CNF()

    # The selected integers sum to zero.
    cnf.extend(PBEnc.equals(lits=indices, weights=list(nums), bound=0, vpool=pool).clauses)

    # Exactly m integers are selected.
    cnf.extend(CardEnc.equals(lits=indices, bound=m, vpool=pool,
                              encoding=EncType.seqcounter).clauses)

    return cnf, {"indices": indices}


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
