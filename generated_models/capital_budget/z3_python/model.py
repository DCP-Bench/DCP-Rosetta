# capital_budget: a Z3 (Python) model from DCP Rosetta.
# Download the `capital_budget.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python capital_budget.py capital_budget.json

import z3


def create_model(instance):
    """A company considers a number of investments, each with a net present value (NPV) and a
    cash outflow now. Choose the investments that maximise the total NPV within the total budget."""
    budget = instance["budget"]        # the total budget available for investment
    npv = instance["npv"]              # npv[i]: the net present value of investment i
    cash_flow = instance["cash_flow"]  # cash_flow[i]: the cash outflow investment i requires now

    # x[i] is true when investment i is chosen
    x = [z3.Bool(f"x_{i}") for i in range(len(npv))]
    # z is the total NPV of the chosen investments
    z = z3.Int("z")

    solver = z3.Optimize()

    # The cash outflow of the chosen investments stays within the budget.
    solver.add(z3.Sum([z3.If(xi, c, 0) for c, xi in zip(cash_flow, x)]) <= budget)

    # The total NPV is the sum of the NPVs of the chosen investments.
    solver.add(z == z3.Sum([z3.If(xi, v, 0) for v, xi in zip(npv, x)]))

    # The total NPV is between 0 and the NPV of all investments together.
    solver.add(z >= 0, z <= sum(npv))

    # Maximise the total NPV.
    solver.maximize(z)

    return solver, {"z": z, "x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
