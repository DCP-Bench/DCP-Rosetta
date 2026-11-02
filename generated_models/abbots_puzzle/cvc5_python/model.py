# abbots_puzzle: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install cvc5 numpy`) with:
#   python abbots_puzzle.py

import cvc5.pythonic as c5


def create_model(instance):
    """100 bushels of corn are distributed among 100 people: each man receives
    three bushels, each woman two and each child half a bushel, and there are
    five times as many women as men. Find the number of men, women and children."""
    # The number of men, of women and of children.
    n_men, n_women, n_children = c5.Ints("n_men n_women n_children")

    solver = c5.Solver()

    solver.add(
        # The counts are not negative.
        n_men >= 0,
        n_women >= 0,
        n_children >= 0,
        # There are 100 people.
        n_men + n_women + n_children == 100,
        # The bushels add up to 100. Counted in half bushels, a man gets 6, a woman 4 and a child 1, 200 in all.
        6 * n_men + 4 * n_women + n_children == 200,
        # There are five times as many women as men.
        n_women == 5 * n_men,
    )
    return solver, {"men": n_men, "women": n_women, "children": n_children}


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
