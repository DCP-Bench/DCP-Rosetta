# session5_grocery: a Paramita (Python) model from DCP Rosetta.
# Download the `session5_grocery.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python session5_grocery.py session5_grocery.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf


def divisors(m):
    """The divisors of m, in increasing order."""
    # small: the divisors up to the square root of m; large: their cofactors m // d, in decreasing order
    small, large = [], []
    # the candidate divisor, tried from 1 up to the square root of m
    d = 1
    while d * d <= m:
        if m % d == 0:
            small.append(d)
            if d * d != m:
                large.append(m // d)
        d += 1
    return small + large[::-1]


def create_model(instance):
    """A kid buys several items. The total price is the same whether the item prices
    are added or multiplied (multiplied in dollars). Find the prices of the items, in cents."""
    total = instance["total_price"]  # the total price, in cents
    n_items = instance["num_items"]  # the number of items the kid buys

    # The product of the prices in dollars equals the total in dollars, so the product of
    # the prices in cents is the total times 100 ** (n_items - 1).
    product = total * 100 ** (n_items - 1)
    # Each price divides the product, and is at most the total, since the prices add up to it.
    divisors_of_product = divisors(product)
    prices_domain = [d for d in divisors_of_product if d <= total]

    # costs[i][d] is true when item i costs d cents
    costs = [{d: Bool(f"item_{i}_costs_{d}") for d in prices_domain} for i in range(n_items)]

    cons = []

    # Each item has exactly one price.
    cons += [sum(costs[i].values()) == 1 for i in range(n_items)]

    # Adding the item prices gives the total price.
    cons += [sum(d * costs[i][d] for i in range(n_items) for d in prices_domain) == total]

    # product_so_far[j][e] is true when the first j prices multiply to e. For j = 1 that is
    # the price of the first item.
    product_so_far = {1: dict(costs[0])}
    for j in range(2, n_items + 1):
        prev = product_so_far[j - 1]  # the products of the first j - 1 prices
        cur = {e: Bool(f"product_of_first_{j}_items_is_{e}") for e in divisors_of_product}  # the products of the first j prices
        product_so_far[j] = cur

        # The first j prices have exactly one product.
        cons.append(sum(cur.values()) == 1)
        for e0 in prev:
            for d in prices_domain:
                e = e0 * d
                if e in divisors_of_product:
                    # Item j costs d, so the product of the first j prices is e0 * d.
                    cons.append(If(prev[e0] & costs[j - 1][d], cur[e]))
                else:
                    # A partial product that does not divide the product cannot reach it.
                    cons.append(~(prev[e0] & costs[j - 1][d]))

    # Multiplying all the prices gives the product.
    cons.append(product_so_far[n_items][product])

    # the price of each item, in cents
    prices = [sum(d * costs[i][d] for d in prices_domain) for i in range(n_items)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in cons:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"prices": prices}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
