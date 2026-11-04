# dinner: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Run it (after `pip install mip numpy`) with:
#   python dinner.py

import mip


def create_model(instance):
    """Twenty people go out to dinner: 1 to 6 grandparents, 1 to 10 parents and 1 to 40
    children. Grandparents cost $3, parents $2 and children $0.50, and the dinner must
    cost $20. How many of each go?"""
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # The number of grandparents, parents and children going to dinner
    grandparents = model.add_var("grandparents", lb=1, ub=6, var_type=mip.INTEGER)
    parents = model.add_var("parents", lb=1, ub=10, var_type=mip.INTEGER)
    children = model.add_var("children", lb=1, ub=40, var_type=mip.INTEGER)

    # There are 20 people at dinner.
    model += mip.xsum([grandparents, parents, children]) == 20

    # The dinner costs $20. Prices are counted in half dollars, so a grandparent is 6,
    # a parent 4, a child 1, and the bill 40.
    model += mip.xsum([6 * grandparents, 4 * parents, children]) == 40

    return model, {
        "grandparents": grandparents,
        "parents": parents,
        "children": children,
    }


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
