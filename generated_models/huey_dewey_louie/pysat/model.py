# huey_dewey_louie: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python huey_dewey_louie.py

from pysat.formula import CNF, IDPool


def create_model(instance):
    """Huey, Dewey and Louie are cub scouts who cannot lie, so each of their statements
    is true. The uncle asks who is guilty."""
    pool = IDPool()

    # huey, dewey and louie are true when that cub is guilty
    huey = pool.id("huey")
    dewey = pool.id("dewey")
    louie = pool.id("louie")

    formula = CNF()
    # Huey: Dewey and Louie are both guilty or both innocent.
    formula.append([-dewey, louie])
    formula.append([dewey, -louie])
    # Dewey: if Huey is guilty, then Dewey is guilty too.
    formula.append([-huey, dewey])
    # Louie: Dewey and Louie are not both guilty.
    formula.append([-dewey, -louie])

    return formula, {"huey": huey, "dewey": dewey, "louie": louie}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

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
