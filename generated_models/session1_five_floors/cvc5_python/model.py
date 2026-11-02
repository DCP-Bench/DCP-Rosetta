# session1_five_floors: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Run it (after `pip install cvc5 numpy`) with:
#   python session1_five_floors.py

import cvc5.pythonic as c5


def create_model(instance):
    """Baker, Cooper, Fletcher, Miller and Smith each live on a different floor
    of a five-floor apartment house. Find the floor of each from the clues."""
    # The floor (1 to 5) where each person lives
    B, C, F, M, S = c5.Ints("B C F M S")

    # The five people
    people = [B, C, F, M, S]

    solver = c5.Solver()

    # They all live on different floors.
    solver.add(c5.Distinct(people))

    # The floors are numbered 1 to 5.
    for p in people:
        solver.add(p >= 1, p <= 5)

    # Baker is not on the fifth floor, Cooper is not on the first, and Fletcher
    # is on neither the first nor the fifth.
    solver.add(B != 5, C != 1, F != 5, F != 1)

    # Miller lives on a higher floor than Cooper.
    solver.add(M > C)

    # Smith does not live on a floor next to Fletcher's.
    solver.add(c5.Or(S - F >= 2, F - S >= 2))

    # Fletcher does not live on a floor next to Cooper's.
    solver.add(c5.Or(F - C >= 2, C - F >= 2))

    return solver, {"B": B, "C": C, "F": F, "M": M, "S": S}


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
