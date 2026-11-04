# contracting_costs: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Run it (after `pip install mip numpy`) with:
#   python contracting_costs.py

import mip


def create_model(instance):
    """A contractor pays each pair of tradesmen a known sum for their services. Find
    what each man charges, so that the two charges in every pair add up to that sum."""
    # The sums paid to the pairs, in dollars: paper hanger and painter, painter and
    # plumber, plumber and electrician, electrician and carpenter, carpenter and mason,
    # mason and painter.
    sums = [1100, 1700, 1100, 3300, 5300, 3200]
    # The largest sum paid to a pair, which is the most any one man charges.
    largest = max(sums)

    model = mip.Model(solver_name="CBC")

    # Each man's charge in dollars, a whole number from 0 up to the largest sum.
    paper_hanger = model.add_var("paper_hanger", lb=0, ub=largest, var_type=mip.INTEGER)
    painter = model.add_var("painter", lb=0, ub=largest, var_type=mip.INTEGER)
    plumber = model.add_var("plumber", lb=0, ub=largest, var_type=mip.INTEGER)
    electrician = model.add_var("electrician", lb=0, ub=largest, var_type=mip.INTEGER)
    carpenter = model.add_var("carpenter", lb=0, ub=largest, var_type=mip.INTEGER)
    mason = model.add_var("mason", lb=0, ub=largest, var_type=mip.INTEGER)

    # Each pair of tradesmen together charges the sum paid to that pair.
    model += paper_hanger + painter == sums[0]
    model += painter + plumber == sums[1]
    model += plumber + electrician == sums[2]
    model += electrician + carpenter == sums[3]
    model += carpenter + mason == sums[4]
    model += mason + painter == sums[5]

    return model, {
        "paper_hanger": paper_hanger,
        "painter": painter,
        "plumber": plumber,
        "electrician": electrician,
        "carpenter": carpenter,
        "mason": mason,
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
