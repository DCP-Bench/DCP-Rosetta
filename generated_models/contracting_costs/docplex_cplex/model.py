# contracting_costs: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python contracting_costs.py

from docplex.mp.model import Model


def create_model(instance):
    """A contractor planning the construction of a house has to pay given totals to pairs of
    tradesmen: what does each man charge for his services?"""
    names = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]

    # What the contractor pays to each pair of tradesmen, in dollars: (first, second, total).
    payments = [("paper_hanger", "painter", 1100),
                ("painter", "plumber", 1700),
                ("plumber", "electrician", 1100),
                ("electrician", "carpenter", 3300),
                ("carpenter", "mason", 5300),
                ("mason", "painter", 3200)]

    # The statement does not say so: a charge is taken to be a positive whole number of dollars.
    # It cannot exceed the largest payment, which is the sum of two positive charges.
    largest_payment = max(total for first, second, total in payments)

    model = Model("contracting_costs")

    # charge[name] is the dollars that the tradesman called name charges
    charge = {name: model.integer_var(1, largest_payment, name=name) for name in names}

    # The contractor pays each pair the sum of the two men's charges.
    model.add_constraints(charge[first] + charge[second] == total for first, second, total in payments)

    return model, charge


if __name__ == "__main__":
    model, outputs = create_model({})
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
