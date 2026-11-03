# huey_dewey_louie: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Run it (after `pip install mip numpy`) with:
#   python huey_dewey_louie.py

import mip


def create_model(instance):
    """Huey, Dewey and Louie are questioned by their uncle. They are cub scouts who cannot lie,
    so each of their three statements is true. Which of them are guilty?"""
    model = mip.Model(solver_name="CBC")

    # Whether each of them is guilty: 1 when guilty, 0 when not.
    huey = model.add_var("huey", var_type=mip.BINARY)
    dewey = model.add_var("dewey", var_type=mip.BINARY)
    louie = model.add_var("louie", var_type=mip.BINARY)

    # Huey: Dewey and Louie are both guilty or both innocent.
    model += dewey - louie == 0
    # Dewey: if Huey is guilty, then so is Dewey.
    model += huey - dewey <= 0
    # Louie: Dewey and Louie are not both guilty.
    model += dewey + louie <= 1

    return model, {"huey": huey, "dewey": dewey, "louie": louie}


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
