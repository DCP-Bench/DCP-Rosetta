# contracting_costs: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Run it (after `pip install exact numpy`) with:
#   python contracting_costs.py

from exact import Exact


def create_model(instance):
    """A contractor paid six tradesmen in pairs, and the bill for each pair is known.
    What does each man charge for his services?"""
    # The six tradesmen.
    men = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]
    # The bill for each pair of tradesmen, in dollars.
    payments = [("paper_hanger", "painter", 1100), ("painter", "plumber", 1700),
                ("plumber", "electrician", 1100), ("electrician", "carpenter", 3300),
                ("carpenter", "mason", 5300), ("mason", "painter", 3200)]

    solver = Exact()

    # Exact identifies its variables by name.
    # charge[m] is what man m charges, in dollars.
    for man in men:
        # A man charges at least a dollar, and less than each pair bill he is part of,
        # since his partner charges at least a dollar too.
        top = min(pay for a, b, pay in payments if man in (a, b)) - 1
        solver.addVariable(man, 1, top)

    # The two men of each pair together charge the bill for that pair.
    for a, b, pay in payments:
        solver.addConstraint([(1, a), (1, b)], True, pay, True, pay)

    return solver, {man: man for man in men}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
