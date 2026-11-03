# session5_grocery: a hermax (Python) model from DCP Rosetta.
# Download the `session5_grocery.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Then run it on the first instance (after `pip install hermax`):
#   python session5_grocery.py session5_grocery.json

from hermax.model import Model


def prime_exponents(n):
    """{prime: exponent} of the positive integer n, by trial division."""
    found = {}
    p = 2
    while p * p <= n:
        while n % p == 0:
            found[p] = found.get(p, 0) + 1
            n //= p
        p += 1
    if n > 1:
        found[n] = found.get(n, 0) + 1
    return found


def divisors_up_to(exponents, limit):
    """Every divisor at most limit of the number with the given {prime: exponent}."""
    divisors = [1]
    for p, e in exponents.items():
        divisors = [d * p ** k for d in divisors for k in range(e + 1) if d * p ** k <= limit]
    return sorted(divisors)


def prime_exponent_in(p, d):
    """How many times the prime p divides the positive integer d."""
    count = 0
    while d % p == 0:
        d //= p
        count += 1
    return count


def create_model(instance):
    """A kid's grocery bill: the cashier added up the prices of the items (in cents) to get
    total_price, but multiplied them by mistake. Find the prices, in cents, such that the
    prices add up to total_price, and such that their product, divided by 100 for every item
    after the first, is total_price as well."""
    total_price = instance["total_price"]  # total_price: the sum of the prices, in cents
    num_items = instance["num_items"]      # num_items: how many items the kid bought

    # The product of the prices is total_price * 100^(num_items - 1) (prices in cents).
    # Every price divides that product, and a price is at most total_price, so each price
    # is one of the divisors of the product up to total_price. Prime exponents of the
    # product: those of total_price, plus 2 and 5 from 100 for each item after the first.
    target = prime_exponents(total_price)
    target[2] = target.get(2, 0) + 2 * (num_items - 1)
    target[5] = target.get(5, 0) + 2 * (num_items - 1)
    candidates = divisors_up_to(target, total_price)

    m = Model()

    # choice[i][k] is true when item i costs candidates[k] cents
    choice = m.bool_matrix("choice", num_items, len(candidates))
    # prices[i] is the price of item i in cents (the declared output)
    prices = [m.int(f"prices_{i}", 1, total_price) for i in range(num_items)]

    for i in range(num_items):
        # Each item has exactly one price, and its price is the candidate it chooses.
        m &= choice.row(i).exactly_one()
        m &= (prices[i] == sum(d * choice[i][k] for k, d in enumerate(candidates)))

    # The prices add up to the total the cashier first charged.
    m &= (sum(prices) == total_price)

    # The prices multiply to the product: for each prime p, the exponents of p in the
    # chosen prices add up to the exponent of p in the product. Only primes that divide
    # the product matter, since every price is one of its divisors.
    for p, e in target.items():
        if e > 0:
            m &= (sum(prime_exponent_in(p, d) * choice[i][k]
                      for i in range(num_items) for k, d in enumerate(candidates)
                      if prime_exponent_in(p, d) > 0) == e)

    return m, {"prices": prices}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
