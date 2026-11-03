# bananas: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
# Run it (after `pip install mip numpy`) with:
#   python bananas.py

import mip


def create_model(instance):
    """Buy 100 fruits for exactly 100 dollars, at least one of each kind, with as few
    bananas and apples as possible. Five bananas cost 3 dollars, seven oranges cost
    5 dollars, nine mangoes cost 7 dollars and three apples cost 9 dollars."""
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Number of bananas, oranges, mangoes and apples bought, each at least one.
    bananas = model.add_var("bananas", lb=1, ub=100, var_type=mip.INTEGER)
    oranges = model.add_var("oranges", lb=1, ub=100, var_type=mip.INTEGER)
    mangoes = model.add_var("mangoes", lb=1, ub=100, var_type=mip.INTEGER)
    apples = model.add_var("apples", lb=1, ub=100, var_type=mip.INTEGER)

    # 100 fruits in total.
    model.add_constr(mip.xsum([bananas, oranges, mangoes, apples]) == 100, "total_fruits")

    # Prices in units of 1/315 dollar, the least common multiple of 5, 7, 9 and 3:
    # a banana is 3/5 dollar (189), an orange 5/7 dollar (225), a mango 7/9 dollar (245),
    # an apple 9/3 dollar (945). The 100 dollars are 31500 units.
    model.add_constr(
        mip.xsum([189 * bananas, 225 * oranges, 245 * mangoes, 945 * apples]) == 31500,
        "total_cost",
    )

    # Fewest bananas and apples.
    model.objective = mip.xsum([bananas, apples])

    return model, {
        "bananas": bananas,
        "oranges": oranges,
        "mangoes": mangoes,
        "apples": apples,
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
