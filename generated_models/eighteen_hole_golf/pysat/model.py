# eighteen_hole_golf: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python eighteen_hole_golf.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """A golf course has 18 holes, each of length 3, 4 or 5, and the total length of the
    course is 72. Find the length of each hole."""
    n_holes = 18        # the course has 18 holes
    total_length = 72   # the length of the course

    pool = IDPool()

    # holes[i] is the length of hole i
    holes = [Integer(f"hole{i}", 3, 5, vpool=pool) for i in range(n_holes)]
    engine = IntegerEngine(vars=holes, vpool=pool)

    # The hole lengths add up to the length of the course.
    engine.add_linear(sum(holes) == total_length)

    return engine.clausify(), {"holes": holes}


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
