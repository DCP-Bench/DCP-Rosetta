# contracting_costs: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Run it (after `pip install cvc5 numpy`) with:
#   python contracting_costs.py

import cvc5.pythonic as c5


def create_model(instance):
    """A contractor planning the construction of a house has to pay six pairs of
    tradesmen a known sum for each pair. What does each man charge for his services?"""
    # The charge of each man in dollars.
    paper_hanger, painter, plumber, electrician, carpenter, mason = c5.Ints(
        "paper_hanger painter plumber electrician carpenter mason"
    )

    solver = c5.Solver()

    # No man charges a negative amount.
    solver.add(
        paper_hanger >= 0,
        painter >= 0,
        plumber >= 0,
        electrician >= 0,
        carpenter >= 0,
        mason >= 0,
    )

    # Each pair of tradesmen together is paid its bill.
    solver.add(
        paper_hanger + painter == 1100,  # $ 1,100 to the paper hanger and the painter
        painter + plumber == 1700,  # $ 1,700 to the painter and the plumber
        plumber + electrician == 1100,  # $ 1,100 to the plumber and the electrician
        electrician + carpenter == 3300,  # $ 3,300 to the electrician and the carpenter
        carpenter + mason == 5300,  # $ 5,300 to the carpenter and the mason
        mason + painter == 3200,  # $ 3,200 to the mason and the painter
    )

    outputs = {
        "paper_hanger": paper_hanger,
        "painter": painter,
        "plumber": plumber,
        "electrician": electrician,
        "carpenter": carpenter,
        "mason": mason,
    }
    return solver, outputs


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
