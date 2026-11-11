# contracting_costs: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python contracting_costs.py

from pycsp3 import *


def create_model(instance):
    """A contractor pays $1,100 to the paper hanger and the painter, $1,700 to the
    painter and plumber, $1,100 to the plumber and electrician, $3,300 to the
    electrician and carpenter, $5,300 to the carpenter and mason and $3,200 to
    the mason and painter. What does each man charge for his services?"""
    # The largest pair payment. Each charge is a part of a pair payment and
    # charges are not negative, so no charge exceeds it.
    largest_payment = 5300

    # The charge of each man for his services, in dollars.
    paper_hanger = Var(dom=range(largest_payment + 1))
    painter = Var(dom=range(largest_payment + 1))
    plumber = Var(dom=range(largest_payment + 1))
    electrician = Var(dom=range(largest_payment + 1))
    carpenter = Var(dom=range(largest_payment + 1))
    mason = Var(dom=range(largest_payment + 1))

    satisfy(
        # The paper hanger and the painter together are paid $1,100.
        paper_hanger + painter == 1100,
        # The painter and the plumber together are paid $1,700.
        painter + plumber == 1700,
        # The plumber and the electrician together are paid $1,100.
        plumber + electrician == 1100,
        # The electrician and the carpenter together are paid $3,300.
        electrician + carpenter == 3300,
        # The carpenter and the mason together are paid $5,300.
        carpenter + mason == 5300,
        # The mason and the painter together are paid $3,200.
        mason + painter == 3200,
    )

    return {
        "paper_hanger": paper_hanger,
        "painter": painter,
        "plumber": plumber,
        "electrician": electrician,
        "carpenter": carpenter,
        "mason": mason,
    }


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
