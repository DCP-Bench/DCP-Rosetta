# contracting_costs: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python contracting_costs.py

from pyscipopt import Model


def create_model(instance):
    """A contractor building a house is told what he would have to pay for each
    pair of the six men on the job: the paper hanger, painter, plumber,
    electrician, carpenter and mason. Find what each man charges for his
    services, in dollars.

    The instance file is empty ([]): every amount is fixed by the statement, so
    the model reads nothing from its argument."""
    model = Model("contracting_costs")

    # Decision variables: the dollars each man charges for his services.
    # They are whole dollars, as the statement asks. No lower bound is set,
    # because the statement does not say that charges are non-negative; the
    # pair sums below fix every value.
    paper_hanger = model.addVar("paper_hanger", vtype="I", lb=None)  # the paper hanger's charge
    painter = model.addVar("painter", vtype="I", lb=None)            # the painter's charge
    plumber = model.addVar("plumber", vtype="I", lb=None)            # the plumber's charge
    electrician = model.addVar("electrician", vtype="I", lb=None)    # the electrician's charge
    carpenter = model.addVar("carpenter", vtype="I", lb=None)        # the carpenter's charge
    mason = model.addVar("mason", vtype="I", lb=None)                # the mason's charge

    # Each pair of men is paid a fixed total, as stated. The six pairs form a
    # connected graph with six men and six pairs, containing an odd cycle
    # (painter, plumber, electrician, carpenter, mason), so these six linear
    # equations have exactly one solution.
    model.addCons(paper_hanger + painter == 1100)      # the paper hanger and the painter: $1,100
    model.addCons(painter + plumber == 1700)           # the painter and the plumber: $1,700
    model.addCons(plumber + electrician == 1100)       # the plumber and the electrician: $1,100
    model.addCons(electrician + carpenter == 3300)     # the electrician and the carpenter: $3,300
    model.addCons(carpenter + mason == 5300)           # the carpenter and the mason: $5,300
    model.addCons(mason + painter == 3200)             # the mason and the painter: $3,200

    # No objective: the statement asks only for the charges that satisfy the pair totals.
    outputs = {
        "carpenter": carpenter,
        "electrician": electrician,
        "mason": mason,
        "painter": painter,
        "paper_hanger": paper_hanger,
        "plumber": plumber,
    }
    return model, outputs


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
