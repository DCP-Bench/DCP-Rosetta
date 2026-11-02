# huey_dewey_louie: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Run it (after `pip install z3-solver numpy`) with:
#   python huey_dewey_louie.py

import z3


def create_model(instance):
    """Huey, Dewey and Louie are cub scouts questioned by their uncle. Cub scouts cannot lie,
    so each of their statements is true. Who is guilty?"""
    # huey, dewey, louie: whether each of them is guilty
    huey, dewey, louie = z3.Bools("huey dewey louie")

    solver = z3.Solver()

    solver.add(
        # Huey: Dewey and Louie have an equal share, so one is guilty exactly when the other is.
        dewey == louie,
        # Dewey: if Huey is guilty, then so am I.
        z3.Implies(huey, dewey),
        # Louie: Dewey and I are not both guilty.
        z3.Not(z3.And(dewey, louie)),
    )

    return solver, {"huey": huey, "dewey": dewey, "louie": louie}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
