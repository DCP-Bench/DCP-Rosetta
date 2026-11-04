# session5_climbing_stairs: a PySAT (Python) model from DCP Rosetta.
# Download the `session5_climbing_stairs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python session5_climbing_stairs.py session5_climbing_stairs.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Climb a stair of n steps, taking between m1 and m2 steps at each move.
    Find the number of steps taken at each move, or 0 once the top is reached."""
    n = instance["n"]    # the number of steps in the stair; each move climbs at least one, so there are at most n moves
    m1 = instance["m1"]  # the fewest steps taken at one move
    m2 = instance["m2"]  # the most steps taken at one move

    pool = IDPool()
    # steps[i] is the number of steps taken at move i, 0 if no move is made
    steps = [Integer(f"steps{i}", 0, m2, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=steps, vpool=pool)

    # The moves add up to the whole stair.
    engine.add_linear(sum(steps) == n)

    cnf = engine.clausify()

    # A move takes between m1 and m2 steps, or none at all.
    for step in steps:
        for value in range(1, m1):
            cnf.append([-step.equals(value)])

    # Once a move takes no steps, the top is reached and every later move takes none too.
    for i in range(1, n):
        cnf.append([-steps[i - 1].equals(0), steps[i].equals(0)])

    return cnf, {"steps": steps}


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
