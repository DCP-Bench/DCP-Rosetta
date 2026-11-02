# dinner: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Run it (after `pip install z3-solver numpy`) with:
#   python dinner.py

import z3


def create_model(instance):
    """Twenty people go out to dinner, grandparents, parents and children, and the
    bill comes to $20: how many of each go?"""
    # How many grandparents, parents and children go to dinner
    grandparents, parents, children = z3.Ints("grandparents parents children")

    solver = z3.Solver()

    # The dinner takes 1 to 6 grandparents, 1 to 10 parents and 1 to 40 children.
    solver.add(
        grandparents >= 1, grandparents <= 6,
        parents >= 1, parents <= 10,
        children >= 1, children <= 40,
    )

    # A grandparent costs $3, a parent $2 and a child $0.50. In half dollars that is
    # 6, 4 and 1, and the bill of $20 is 40 half dollars.
    solver.add(6 * grandparents + 4 * parents + 1 * children == 40)

    # There are 20 people at dinner.
    solver.add(grandparents + parents + children == 20)

    return solver, {"grandparents": grandparents, "parents": parents, "children": children}


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
