# session5_grocery: a PySAT (Python) model from DCP Rosetta.
# Download the `session5_grocery.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python session5_grocery.py session5_grocery.json

from pysat.formula import IDPool
from pysat.pb import PBEnc
from pysat.integer import Integer, IntegerEngine


def divisors(value):
    """The divisors of value, found by trial division up to its square root."""
    found = set()  # the divisors found so far
    d = 1
    while d * d <= value:
        if value % d == 0:
            found.update((d, value // d))
        d += 1
    return sorted(found)


def create_model(instance):
    """A kid buys several items. The cashier first multiplies the item prices and then adds
    them, and both give the same total price. Find the prices of the items, in cents."""
    total_price = instance["total_price"]  # the total price, in cents
    num_items = instance["num_items"]      # the number of items bought

    # Multiplying the prices in euros gives the total in euros. In cents the product is
    # 100 times the total for each item after the first.
    target = total_price * 100 ** (num_items - 1)
    divs = divisors(target)
    allowed = [v for v in divs if v <= total_price]  # the prices that can occur

    pool = IDPool()
    # prices[k] is the price of item k, in cents, between 1 and the total price
    prices = [Integer(f"price{k}", 1, total_price, vpool=pool) for k in range(num_items)]
    engine = IntegerEngine(vars=prices, vpool=pool)
    cnf = engine.clausify()

    # Each price divides the target, since the prices multiply to it. A price that does not
    # divide it is ruled out.
    for item in prices:
        for value in range(1, total_price + 1):
            if target % value != 0:
                cnf.append([-item.equals(value)])

    # The prices add up to the total price.
    lits = [item.equals(v) for item in prices for v in allowed]
    weights = [v for _ in prices for v in allowed]
    cnf.extend(PBEnc.equals(lits=lits, weights=weights, bound=total_price, vpool=pool).clauses)

    # The prices multiply to the target. product_so_far[d] is true when the prices seen so far
    # multiply to d. Each new price multiplies the product so far; a product that no longer
    # divides the target is ruled out.
    product_so_far = {v: prices[0].equals(v) for v in allowed}
    for k in range(1, num_items):
        product_with_next = {d: pool.id(("product", k, d)) for d in divs}
        for d, so_far in product_so_far.items():
            for v in allowed:
                if target % (d * v) == 0:
                    cnf.append([-so_far, -prices[k].equals(v), product_with_next[d * v]])
                else:
                    cnf.append([-so_far, -prices[k].equals(v)])
        product_so_far = product_with_next
    # The product of all the prices is the target.
    for d, product in product_so_far.items():
        if d != target:
            cnf.append([-product])

    return cnf, {"prices": prices}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
