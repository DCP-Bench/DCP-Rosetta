# contracting_costs: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Run it (after `pip install z3-solver numpy`) with:
#   python contracting_costs.py

import z3


def create_model(instance):
    """A contractor planning the construction of a house has to pay six pairs of
    tradesmen a known sum for each pair. What does each man charge for his services?"""
    # Each man's charge for his services, in dollars.
    paper_hanger, painter, plumber, electrician, carpenter, mason = men = z3.Ints(
        "paper_hanger painter plumber electrician carpenter mason")

    # The two men of each pair, and the bill the contractor pays for that pair in dollars.
    pair_bills = [
        (paper_hanger, painter, 1100),
        (painter, plumber, 1700),
        (plumber, electrician, 1100),
        (electrician, carpenter, 3300),
        (carpenter, mason, 5300),
        (mason, painter, 3200),
    ]

    # No man charges less than 1 dollar or more than the largest bill.
    largest = max(bill for _, _, bill in pair_bills)
    solver = z3.Solver()

    solver.add([z3.And(man >= 1, man <= largest) for man in men])

    # The two men of each pair together charge the bill for that pair.
    solver.add([first + second == bill for first, second, bill in pair_bills])

    return solver, {
        "paper_hanger": paper_hanger,
        "painter": painter,
        "plumber": plumber,
        "electrician": electrician,
        "carpenter": carpenter,
        "mason": mason,
    }


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
