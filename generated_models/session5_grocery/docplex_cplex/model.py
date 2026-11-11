# session5_grocery: a CPLEX (Python) model from DCP Rosetta.
# Download the `session5_grocery.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python session5_grocery.py session5_grocery.json

from docplex.mp.model import Model


def create_model(instance):
    """Grocery: a kid buys num_items items. Each price is a positive whole number of cents, and
    both the sum and the product of the prices in dollars equal the total price in dollars."""
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
    total = instance["total_price"]  # what the cashier charges, in cents
    count = instance["num_items"]    # how many items the kid bought
    items = range(count)
    cents_per_dollar = 100
    # The prices in dollars multiply to the total in dollars. In cents, each price after the
    # first adds a factor of 100, so the prices in cents multiply to total * 100 ** (count - 1).
    product = total * cents_per_dollar ** (count - 1)

    # The product of positive integers equals `product` exactly when each of them
    # divides it and, for every prime, their exponents add up to its exponent.
    # That turns the product into linear constraints over the divisors; CPLEX
    # would refuse the product itself as a non-convex constraint.
    primes = factorise(product)
    # A price divides the product, and is at most total because the positive prices add up to total.
    divisors = [d for d in range(1, total + 1) if product % d == 0]
    exponent = {d: factorise(d) for d in divisors}  # exponent[d][p]: the power of prime p in d

    model = Model("grocery")

    # costs[i, d] is 1 when item i costs d cents.
    costs = model.binary_var_matrix(items, divisors, name="costs")
    # Each item has exactly one price.
    model.add_constraints(model.sum(costs[i, d] for d in divisors) == 1 for i in items)

    # Adding the prices gives the total.
    model.add_constraint(model.sum(d * costs[i, d] for i in items for d in divisors) == total, ctname="sum")

    # Multiplying the prices gives the scaled total, prime by prime.
    for p, power in primes.items():
        model.add_constraint(model.sum(exponent[d].get(p, 0) * costs[i, d] for i in items for d in divisors)
                             == power, ctname=f"product_{p}")

    # prices[i] is the price of item i, in cents.
    return model, {"prices": [model.sum(d * costs[i, d] for d in divisors) for i in items]}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
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
