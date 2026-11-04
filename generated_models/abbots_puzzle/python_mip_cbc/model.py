# abbots_puzzle: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install mip numpy`) with:
#   python abbots_puzzle.py

import mip


def create_model(instance):
    """100 bushels of corn are shared among 100 people: each man gets three
    bushels, each woman two and each child half a bushel. There are five times
    as many women as men. Find the number of men, women and children."""
    model = mip.Model(solver_name="CBC")

    # The numbers of men, women and children, each from 0 to 100.
    men = model.add_var("men", lb=0, ub=100, var_type=mip.INTEGER)
    women = model.add_var("women", lb=0, ub=100, var_type=mip.INTEGER)
    children = model.add_var("children", lb=0, ub=100, var_type=mip.INTEGER)

    # There are 100 people.
    model.add_constr(men + women + children == 100)

    # The corn comes to 100 bushels. Counted in half bushels, a man takes 6, a woman 4 and a child 1, for 200 in all.
    model.add_constr(6 * men + 4 * women + children == 200)

    # There are five times as many women as men.
    model.add_constr(women == 5 * men)

    return model, {"men": men, "women": women, "children": children}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
