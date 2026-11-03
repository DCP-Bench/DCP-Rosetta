# dinner: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Run it (after `pip install cvc5 numpy`) with:
#   python dinner.py

import cvc5.pythonic as c5


def create_model(instance):
    """Twenty people go to dinner, grandparents, parents and children, and the
    bill is $20: how many of each go?"""
    # The numbers of grandparents, parents and children going to dinner
    grandparents, parents, children = c5.Ints("grandparents parents children")

    solver = c5.Solver()

    # Between 1 and 6 grandparents, 1 and 10 parents and 1 and 40 children go.
    solver.add(
        grandparents >= 1, grandparents <= 6,
        parents >= 1, parents <= 10,
        children >= 1, children <= 40,
    )

    # There are 20 people in total.
    solver.add(grandparents + parents + children == 20)

    # The bill is 2000 cents. A grandparent costs 300 cents, a parent 200 and a child 50.
    solver.add(300 * grandparents + 200 * parents + 50 * children == 2000)

    return solver, {"grandparents": grandparents, "parents": parents, "children": children}


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
