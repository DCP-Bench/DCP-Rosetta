# contracting_costs: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python contracting_costs.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

# The six tradesmen, in the order of the statement.
NAMES = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]
# Each pair of tradesmen, and the dollars paid to the two of them together.
PAYMENTS = [("paper_hanger", "painter", 1100), ("painter", "plumber", 1700),
            ("plumber", "electrician", 1100), ("electrician", "carpenter", 3300),
            ("carpenter", "mason", 5300), ("mason", "painter", 3200)]


def create_model(instance):
    """A contractor has to pay six pairs of tradesmen a known sum for each pair.
    What does each man charge for his services?"""
    pool = IDPool()

    # The other man in each pair charges at least a dollar, so a man charges less than
    # the smallest sum paid to a pair he belongs to.
    top = {name: min(pay for a, b, pay in PAYMENTS if name in (a, b)) - 1 for name in NAMES}
    # charge[name] is what the tradesman charges, in whole dollars.
    charge = {name: Integer(name, 1, top[name], vpool=pool) for name in NAMES}
    # Each man charges exactly one amount within his range.
    engine = IntegerEngine(vars=list(charge.values()), vpool=pool)
    formula = engine.clausify()

    # Each pair is paid its sum together. Once the first man's charge is fixed, the second
    # man's charge is the rest of the sum, and a first charge that leaves no possible rest
    # is ruled out.
    for a, b, pay in PAYMENTS:
        for value in range(1, top[a] + 1):
            rest = pay - value
            if 1 <= rest <= top[b]:
                formula.append([-charge[a].equals(value), charge[b].equals(rest)])
            else:
                formula.append([-charge[a].equals(value)])

    return formula, charge


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
