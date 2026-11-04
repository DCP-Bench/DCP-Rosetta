# eighteen_hole_golf: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Run it (after `pip install mip numpy`) with:
#   python eighteen_hole_golf.py

import mip


def create_model(instance):
    """Generate an 18-hole golf course where each hole has a length of 3, 4, or 5,
    and the total length of the course is 72."""
    n_holes = 18  # the number of holes on the course
    total_length = 72  # the length of the whole course

    model = mip.Model(solver_name="CBC")

    # holes[i] is the length of hole i, one of 3, 4 or 5
    holes = [model.add_var(f"hole_{i}", lb=3, ub=5, var_type=mip.INTEGER) for i in range(n_holes)]

    # The hole lengths add up to the length of the course.
    model += mip.xsum(holes) == total_length

    return model, {"holes": holes}


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
