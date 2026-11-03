# curious_set_of_integers: a PySAT (Python) model from DCP Rosetta.
# Download the `curious_set_of_integers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python curious_set_of_integers.py curious_set_of_integers.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """The integers 1, 3, 8 and 120 form a set in which the product of any two
    integers is one less than a perfect square. Find a fifth number (at least 0)
    that can be added to the set without destroying this property."""
    n_integers = instance["n"]     # the number of integers in the set, the four given ones and the one to find
    max_val = instance["max_val"]  # the largest value any integer in the set may take
    members = [1, 3, 8, 120]       # the four given integers
    assert n_integers == len(members) + 1, "the problem adds exactly one number to the four given ones"

    pool = IDPool()

    # The number to add to the set
    number = Integer("number", 0, max_val, vpool=pool)
    # root[member] is the square root of member times the number, plus 1
    root = {member: Integer(f"root{member}", 0, max_val, vpool=pool) for member in members}
    engine = IntegerEngine(vars=[number] + list(root.values()), vpool=pool)
    formula = engine.clausify()

    # The new number differs from the four given integers.
    for member in members:
        if member <= max_val:
            formula.append([-number.equals(member)])

    # For each given integer, its product with the new number is one less than a perfect
    # square. PySAT cannot multiply two variables, so both sides are listed by value: a flag
    # for each value, set when the square or the product takes that value. At most one flag
    # is set, so both sides take the same value.
    for member in members:
        # value_is[v] is the flag of the value v
        value_is = {}
        for p in range(max_val + 1):
            if p * p not in value_is:
                value_is[p * p] = pool.id(("value", member, p * p))
            formula.append([-root[member].equals(p), value_is[p * p]])
        for w in range(max_val + 1):
            if member * w + 1 not in value_is:
                value_is[member * w + 1] = pool.id(("value", member, member * w + 1))
            formula.append([-number.equals(w), value_is[member * w + 1]])
        formula.extend(CardEnc.atmost(lits=list(value_is.values()), bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    return formula, {"number": number}


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
