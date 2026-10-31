from hermax.model import Model


def build(instance):
    # Contracting costs problem: find what each contractor charges.
    # Given pairs of contractors and their combined cost:
    # paper_hanger + painter = 1,100
    # painter + plumber = 1,700
    # plumber + electrician = 1,100
    # electrician + carpenter = 3,300
    # carpenter + mason = 5,300
    # mason + painter = 3,200

    m = Model()

    # Cost of each contractor (all positive integers in dollars)
    # Reasonable upper bound: any single contractor costs at most 5000
    max_cost = 5000

    paper_hanger = m.int("paper_hanger", 0, max_cost)
    painter = m.int("painter", 0, max_cost)
    plumber = m.int("plumber", 0, max_cost)
    electrician = m.int("electrician", 0, max_cost)
    carpenter = m.int("carpenter", 0, max_cost)
    mason = m.int("mason", 0, max_cost)

    # Constraints: pairs of contractors and their combined cost
    m &= (paper_hanger + painter == 1100)
    m &= (painter + plumber == 1700)
    m &= (plumber + electrician == 1100)
    m &= (electrician + carpenter == 3300)
    m &= (carpenter + mason == 5300)
    m &= (mason + painter == 3200)

    return m, {
        "paper_hanger": paper_hanger,
        "carpenter": carpenter,
        "electrician": electrician,
        "mason": mason,
        "painter": painter,
        "plumber": plumber,
    }
