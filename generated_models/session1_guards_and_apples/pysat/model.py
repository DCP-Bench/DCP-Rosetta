# session1_guards_and_apples: a PySAT (Python) model from DCP Rosetta.
# Download the `session1_guards_and_apples.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python session1_guards_and_apples.py session1_guards_and_apples.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """A boy passes through a number of gates to give an apple to a girl. At each
    gate he gives the guard half of his apples plus one, always a whole number of
    apples, and after the last gate he has one apple left for the girl. Find how
    many apples he has when he reaches each gate, and how many is left at the end."""
    num_gates = instance["num_gates"]  # the number of gates, each with a guard

    pool = IDPool()
    # apples[i] is the number of apples the boy has when he reaches gate i, gates counted
    # from 0. The last entry is what he has after the last gate: the one apple for the girl.
    apples = [Integer(f"apples_{i}", 0, 100, vpool=pool) for i in range(num_gates)]
    apples.append(Integer(f"apples_{num_gates}", 1, 1, vpool=pool))
    engine = IntegerEngine(vars=apples, vpool=pool)

    # At each gate the boy gives the guard half of his apples plus one, so before the gate
    # he had twice what was left after it, plus two.
    for i in range(num_gates):
        engine.add_linear(apples[i] == 2 * apples[i + 1] + 2)

    return engine.clausify(), {"apples": apples}


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
