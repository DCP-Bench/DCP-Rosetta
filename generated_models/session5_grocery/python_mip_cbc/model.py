# session5_grocery: a Python-MIP (Python) model from DCP Rosetta.
# Download the `session5_grocery.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python session5_grocery.py session5_grocery.json

import mip


def _prime_exponents(n):
    """The power of each prime that divides n, as a dict from prime to power."""
    exps = {}
    q = 2
    while q * q <= n:
        while n % q == 0:
            exps[q] = exps.get(q, 0) + 1
            n //= q
        q += 1
    if n > 1:
        exps[n] = exps.get(n, 0) + 1
    return exps


def create_model(instance):
    """A kid buys several items. The cashier first multiplies the item prices and
    then adds them, and both give the same total price. Find the prices of the items, in cents."""
    n_items = instance["num_items"]  # the number of items bought
    total = instance["total_price"]  # the total price, in cents

    model = mip.Model(solver_name="CBC")

    # Multiplied in dollars, the prices give the total in dollars. In cents, the product
    # is 100 to the power n_items - 1 times the total.
    product = total * 100 ** (n_items - 1)
    product_exps = _prime_exponents(product)

    # The candidate prices: the numbers up to the total that divide the product.
    divisors = [d for d in range(1, total + 1) if product % d == 0]
    # exps[d] holds the power of each prime in the candidate price d.
    exps = {d: _prime_exponents(d) for d in divisors}

    # pick[i][d] is 1 when item i costs d cents, and 0 when not.
    pick = [
        {d: model.add_var(name=f"pick_{i}_{d}", var_type=mip.BINARY) for d in divisors}
        for i in range(n_items)
    ]
    # price[i] is the price of item i, in cents.
    price = [mip.xsum(d * pick[i][d] for d in divisors) for i in range(n_items)]

    # Each item costs exactly one of the candidate prices.
    for i in range(n_items):
        model.add_constr(mip.xsum(pick[i][d] for d in divisors) == 1)

    # The item prices add up to the total price.
    model.add_constr(mip.xsum(price) == total)

    # The prices multiply to the product. For each prime, the powers of that prime in
    # the prices add up to its power in the product.
    for q, target in product_exps.items():
        model.add_constr(
            mip.xsum(
                exps[d].get(q, 0) * pick[i][d]
                for i in range(n_items)
                for d in divisors
            )
            == target
        )

    return model, {"prices": price}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
