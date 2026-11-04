# contracting_costs: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Run it (after `pip install hermax`) with:
#   python contracting_costs.py
from hermax.model import Model

# The problem fixes its data, so the instance carries no fields.
# The six tradesmen, in the order the outputs are reported.
NAMES = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]
# (first man, second man, dollars paid to the two of them together)
PAYMENTS = [("paper_hanger", "painter", 1100), ("painter", "plumber", 1700),
            ("plumber", "electrician", 1100), ("electrician", "carpenter", 3300),
            ("carpenter", "mason", 5300), ("mason", "painter", 3200)]
# No charge can exceed the largest payment, since the partner's charge is not negative.
LARGEST_PAYMENT = max(pay for _, _, pay in PAYMENTS)


def create_model(instance):
    """Find what each of six tradesmen charges, given the sum paid for each pair of them.
    A satisfaction problem: there is no objective, the model only has to fix the charges."""
    # The instance has no fields; all data is fixed by the problem statement above.
    m = Model()

    # charge[name] is what that man charges for his services, in dollars (0 up to the largest payment)
    charge = {name: m.int(name, 0, LARGEST_PAYMENT) for name in NAMES}

    # Each pair of men is paid the given amount together: their two charges sum to that payment.
    for first, second, pay in PAYMENTS:
        m &= (charge[first] + charge[second] == pay)

    return m, charge


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
