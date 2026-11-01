# contracting_costs: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Run it (after `pip install ortools`) with:
#   python contracting_costs.py

from ortools.sat.python import cp_model


def create_model(instance):
    """A contractor planning the construction of a house has to pay six pairs of
    tradesmen a known sum for each pair. What does each man charge for his services?"""
    # The six bills in dollars, one for each pair of men, in the order of the statement.
    bills = [1100, 1700, 1100, 3300, 5300, 3200]
    # The largest bill; no man charges more than this.
    largest = max(bills)

    model = cp_model.CpModel()

    # The six men's charges in dollars, each at least 1 and at most the largest bill.
    paper_hanger = model.new_int_var(1, largest, "paper_hanger")
    painter = model.new_int_var(1, largest, "painter")
    plumber = model.new_int_var(1, largest, "plumber")
    electrician = model.new_int_var(1, largest, "electrician")
    carpenter = model.new_int_var(1, largest, "carpenter")
    mason = model.new_int_var(1, largest, "mason")

    # Each pair's two charges add up to its bill.
    model.add(paper_hanger + painter == bills[0])
    model.add(painter + plumber == bills[1])
    model.add(plumber + electrician == bills[2])
    model.add(electrician + carpenter == bills[3])
    model.add(carpenter + mason == bills[4])
    model.add(mason + painter == bills[5])

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
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
