# contracting_costs: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Run it (after `pip install cpmpy`) with:
#   python contracting_costs.py

import cpmpy as cp


def create_model(instance):
    """A contractor has to pay six pairs of tradesmen a known sum for each pair.
    What does each man charge for his services?"""
    # The statement fixes all the data, so the instance is empty.

    # charge[i] is what tradesman i charges in dollars; no charge exceeds the largest
    # bill, 5300, and each charge is at least 1
    charge = cp.intvar(1, 5300, shape=6, name="charge")
    paper_hanger, painter, plumber, electrician, carpenter, mason = charge

    model = cp.Model()
    # Each pair of tradesmen together is paid the stated bill.
    model.add(paper_hanger + painter == 1100)
    model.add(painter + plumber == 1700)
    model.add(plumber + electrician == 1100)
    model.add(electrician + carpenter == 3300)
    model.add(carpenter + mason == 5300)
    model.add(mason + painter == 3200)

    return model, {
        "paper_hanger": paper_hanger,
        "painter": painter,
        "plumber": plumber,
        "electrician": electrician,
        "carpenter": carpenter,
        "mason": mason,
    }


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
