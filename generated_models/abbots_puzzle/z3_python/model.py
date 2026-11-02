# abbots_puzzle: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install z3-solver numpy`) with:
#   python abbots_puzzle.py

import z3


def create_model(instance):
    """100 bushels of corn are distributed among 100 people: each man receives
    three bushels, each woman two and each child half a bushel, and there are
    five times as many women as men. Find the number of men, women and children."""
    # The puzzle states all its numbers, so the instance holds no data.

    # The number of men, women and children.
    n_men = z3.Int("men")
    n_women = z3.Int("women")
    n_children = z3.Int("children")

    solver = z3.Solver()

    # Each group has between 0 and 100 people.
    solver.add(n_men >= 0, n_women >= 0, n_children >= 0,
               n_men <= 100, n_women <= 100, n_children <= 100)

    # There are 100 people.
    solver.add(n_men + n_women + n_children == 100)

    # The bushels add up to 100. Each man gets 3, each woman 2 and each child half a bushel,
    # so counted in half bushels a man is 6, a woman 4 and a child 1, and the total is 200.
    solver.add(n_men * 6 + n_women * 4 + n_children == 200)

    # There are five times as many women as men.
    solver.add(n_women == n_men * 5)

    return solver, {"men": n_men, "women": n_women, "children": n_children}


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
