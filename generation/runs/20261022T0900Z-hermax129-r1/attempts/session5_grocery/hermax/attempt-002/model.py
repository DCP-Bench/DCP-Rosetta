from hermax.model import Model


def _factorize(x):
    """Prime factorisation of a positive integer by trial division."""
    factors = {}
    d = 2
    while d * d <= x:
        while x % d == 0:
            factors[d] = factors.get(d, 0) + 1
            x //= d
        d += 1
    if x > 1:
        factors[x] = factors.get(x, 0) + 1
    return factors


def _divisors_up_to(factors, limit):
    """Divisors of the number with the given factorisation that are <= limit."""
    divs = [1]
    for p, e in factors.items():
        grown = []
        for d in divs:
            v = d
            for _ in range(e + 1):
                if v > limit:
                    break
                grown.append(v)
                v *= p
        divs = grown
    return sorted(divs)


def _exponent(x, p):
    e = 0
    while x % p == 0:
        x //= p
        e += 1
    return e


def build(instance):
    n = int(instance["num_items"])
    total = int(instance["total_price"])

    # Product of the prices in cents must be total * 100^(n-1).
    factors = _factorize(total)
    for p in (2, 5):
        factors[p] = factors.get(p, 0) + 2 * (n - 1)
    factors = {p: e for p, e in factors.items() if e > 0}

    # Every price is a divisor of that product and at most the total.
    divs = _divisors_up_to(factors, total)
    K = len(divs)

    m = Model()
    picks = [m.bool_vector(f"pick{i}", K) for i in range(n)]
    prices = []
    for i in range(n):
        # Each item costs exactly one of the candidate divisors.
        m &= picks[i].exactly_one()
        price = m.int(f"price{i}", 0, total)
        m &= (price == sum(divs[k] * picks[i][k] for k in range(K)))
        prices.append(price)

    # The additive total: the prices add up to the total price.
    m &= (sum(divs[k] * picks[i][k] for i in range(n) for k in range(K)) == total)

    # The multiplicative total: for each prime p, the exponents of p in the
    # chosen prices add up to the exponent of p in total * 100^(n-1).
    for p, e in factors.items():
        terms = []
        for k, d in enumerate(divs):
            v = _exponent(d, p)
            if v:
                for i in range(n):
                    terms.append(v * picks[i][k])
        if terms:
            m &= (sum(terms) == e)
        else:
            # No candidate price carries p, so no solution exists.
            dead = m.bool()
            m &= dead
            m &= ~dead

    return m, {"prices": prices}
