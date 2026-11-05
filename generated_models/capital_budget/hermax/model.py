# capital_budget: a hermax (Python) model from DCP Rosetta.
# Download the `capital_budget.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
# Then run it on the first instance (after `pip install hermax`):
#   python capital_budget.py capital_budget.json

from hermax.model import Model


def create_model(instance):
    """Capital budgeting: a company considers a number of investments. Each investment
    yields a net present value (NPV) and needs a cash outflow now. Choose investments
    whose total cash outflow fits within the budget so that the total NPV is as large
    as possible."""
    budget = instance["budget"]          # the total cash available for investment
    cash_flow = instance["cash_flow"]    # cash_flow[i]: the cash outflow investment i requires now
    npv = instance["npv"]                # npv[i]: the net present value investment i yields
    n = len(npv)                         # the number of investments

    m = Model()

    # x[i] is true when investment i is chosen
    x = m.bool_vector("x", n)

    # The cash outflows of the chosen investments add up to no more than the budget.
    m &= (sum(cash_flow[i] * x[i] for i in range(n)) <= budget)

    # z is the total NPV of the chosen investments.
    z = sum(npv[i] * x[i] for i in range(n))

    # Maximise the total NPV. hermax always minimises, so minimise its negation.
    m.obj += -z

    # The objective in the problem's terms: the total NPV z, whose negation the solver minimises.
    return m, {"x": x, "z": z}, z


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
