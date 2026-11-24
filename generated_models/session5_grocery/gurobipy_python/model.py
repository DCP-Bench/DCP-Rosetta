# session5_grocery: a Gurobi (Python) model from DCP Rosetta.
# Download the `session5_grocery.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python session5_grocery.py session5_grocery.json

import gurobipy as gp
from gurobipy import GRB


def factorise(number):
    """The prime factorisation of a positive integer, as {prime: exponent}."""
    factors, prime = {}, 2
    while prime * prime <= number:
        while number % prime == 0:
            factors[prime] = factors.get(prime, 0) + 1
            number //= prime
        prime += 1
    if number > 1:
        factors[number] = factors.get(number, 0) + 1
    return factors


def create_model(instance):
    """Grocery: find the prices of some items, in cents, whose sum and whose product (each price taken in dollars) are both the total price."""
    total = instance["total_price"]  # the total price, in cents
    count = instance["num_items"]    # the number of items bought
    items = range(count)
    # Multiplying the prices in dollars gives the total in dollars. In cents, the product of the prices
    # is then the total times 100 for each factor after the first, that is total * 100 ** (count - 1).
    product = total * 100 ** (count - 1)

    # Each price is a divisor of the product, and at most the total: prices are positive and add up to the total.
    # Not from the statement: a price cannot exceed the total, so only these divisors are candidates.
    primes = factorise(product)
    divisors = [d for d in range(1, total + 1) if product % d == 0]
    exponent = {d: factorise(d) for d in divisors}

    model = gp.Model("grocery")

    # costs[i, d] is 1 when item i costs d cents, and 0 when not.
    costs = model.addVars(items, divisors, vtype=GRB.BINARY, name="costs")
    # Each item has exactly one price.
    model.addConstrs((costs.sum(i, "*") == 1 for i in items), name="one_price")

    # Adding the prices gives the total.
    model.addConstr(gp.quicksum(d * costs[i, d] for i in items for d in divisors) == total, name="sum")

    # Multiplying the prices gives the product. The prices multiply to the product exactly when, for each prime,
    # the exponents of that prime in the prices add up to its exponent in the product. That is linear, so one
    # constraint per prime replaces the product.
    model.addConstrs((gp.quicksum(exponent[d].get(p, 0) * costs[i, d] for i in items for d in divisors) == power
                      for p, power in primes.items()), name="product")

    # No objective: any prices that meet both constraints answer the puzzle.
    return model, {"prices": [gp.quicksum(d * costs[i, d] for d in divisors) for i in items]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
