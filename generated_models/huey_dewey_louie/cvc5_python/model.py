# huey_dewey_louie: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Run it (after `pip install cvc5 numpy`) with:
#   python huey_dewey_louie.py

import cvc5.pythonic as c5


def create_model(instance):
    """Huey, Dewey and Louie are questioned by their uncle. They are cub scouts and
    cannot lie, so each of their statements is true. Who is guilty?"""
    # huey, dewey, louie: whether each of them is guilty
    huey, dewey, louie = c5.Bools("huey dewey louie")

    solver = c5.Solver()

    solver.add(
        # Huey: Dewey and Louie have an equal share; if one is guilty, so is the other.
        dewey == louie,
        # Dewey: if Huey is guilty, then so am I.
        c5.Implies(huey, dewey),
        # Louie: Dewey and I are not both guilty.
        c5.Not(c5.And(dewey, louie)),
    )

    return solver, {"huey": huey, "dewey": dewey, "louie": louie}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
