from hermax.model import Model


def prime_factors(n):
    # Trial division: returns {prime: exponent}.
    out = {}
    p = 2
    while p * p <= n:
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
        p += 1
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def build(instance):
    total = instance["total_price"]
    n = instance["num_items"]

    # Prices are in cents, but the cashier multiplies the prices in dollars and
    # reports the result in cents. Multiplying the prices in cents gives
    # total * 100**(n-1), so that is the target product N.
    target = total * 100 ** (n - 1)

    # Every price divides N and is at most the total (all prices are at least 1
    # and they sum to the total). Only these candidate values are needed.
    candidates = [d for d in range(1, total + 1) if target % d == 0]

    # Exponent of each prime of N in each candidate.
    primes = prime_factors(target)
    exps = {p: [] for p in primes}
    for d in candidates:
        for p in primes:
            e, x = 0, d
            while x % p == 0:
                e, x = e + 1, x // p
            exps[p].append(e)

    m = Model()

    # choice[i][c] is true when item i costs candidates[c].
    choice = m.bool_matrix("choice", n, len(candidates))
    for i in range(n):
        m &= choice.row(i).exactly_one()

    # Each price is the candidate its choice selects, written as a weighted sum
    # of the item's choices.
    prices = [sum(d * choice[i][c] for c, d in enumerate(candidates))
              for i in range(n)]

    # The items add up to the total price.
    m &= (sum(prices) == total)

    # The product of the prices equals N, which holds exactly when each prime
    # exponent of N is the sum of the exponents of the chosen prices.
    for p in primes:
        m &= (sum(exps[p][c] * choice[i][c]
                  for i in range(n) for c in range(len(candidates)))
              == primes[p])

    return m, {"prices": prices}
