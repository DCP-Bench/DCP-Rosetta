# session5_grocery: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `session5_grocery.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Then run it on the first instance (after `pip install ortools`):
#   python session5_grocery.py session5_grocery.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A kid buys several items. The cashier first multiplies the item prices and
    then adds them, and both give the same total price. Find the prices of the items, in cents."""
    total = instance["total_price"]  # the total price, in cents
    n_items = instance["num_items"]  # the number of items bought

    model = cp_model.CpModel()

    # prices[i] is the price of item i, in cents
    prices = [model.new_int_var(1, total, f"price_{i}") for i in range(n_items)]
    # product is the product of all the prices
    product = model.new_int_var(1, total ** n_items, "product")
    model.add_multiplication_equality(product, prices)

    # Adding the prices gives the total.
    model.add(sum(prices) == total)

    # Multiplying the prices gives the total too, when the prices are read in dollars.
    # In cents, the product is 100 ** (n_items - 1) times the total.
    model.add(product == total * 100 ** (n_items - 1))

    return model, {"prices": prices}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
