# clock_triplets: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python clock_triplets.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Arrange the numbers 1 to 12 on the face of a clock so that no three neighbouring
    numbers add up to more than 21, the smallest value the largest such sum can take."""
    n_numbers = 12  # the numbers on the clock face, 1 to 12
    max_sum = 21    # the most that three neighbouring numbers may add up to

    pool = IDPool()

    # x[i] is the number at position i of the clock face
    x = [Integer(f"x_{i}", 1, n_numbers, vpool=pool) for i in range(n_numbers)]
    engine = IntegerEngine(vars=x, vpool=pool)

    # Each of the numbers 1 to 12 appears exactly once.
    engine.add_alldifferent(x)

    # Every three neighbouring positions, going round the face, add up to at most 21.
    for i in range(n_numbers):
        engine.add_linear(x[i] + x[(i + 1) % n_numbers] + x[(i + 2) % n_numbers] <= max_sum)

    return engine.clausify(), {"x": x}


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
