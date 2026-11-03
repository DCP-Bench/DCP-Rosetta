# fancy_dress: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python fancy_dress.py

from pysat.formula import IDPool, WCNF


def create_model(instance):
    """Mr Greenguest wants to attend a party where guests must wear green. He owns
    only a green shirt, and can buy a green tie, a green hat and green socks, or
    pay the entrance fee instead of following the dress rules. Find the cheapest way."""
    pool = IDPool()
    # t is true when he wears a green tie
    t = pool.id("tie")
    # h is true when he wears a green hat
    h = pool.id("hat")
    # r is true when he wears a green shirt, which he already owns
    r = pool.id("shirt")
    # s is true when he wears green socks
    s = pool.id("socks")
    # n is true when he pays the entrance fee
    n = pool.id("fee")

    formula = WCNF()

    # Without paying the fee, he has to follow the three dress rules.
    # Rule 1: a green tie requires a green shirt.
    formula.append([-t, r, n])
    # Rule 2: green socks or a green shirt require a green tie or a green hat.
    formula.append([-s, t, h, n])
    formula.append([-r, t, h, n])
    # Rule 3: a green shirt, a green hat, or no green socks require a green tie.
    formula.append([-r, t, n])
    formula.append([-h, t, n])
    formula.append([s, t, n])

    # Each item he buys costs its price (tie 10, hat 2, socks 12), and the fee costs 11.
    # The shirt is already owned, so it costs nothing.
    formula.append([-t], weight=10)
    formula.append([-h], weight=2)
    formula.append([-s], weight=12)
    formula.append([-n], weight=11)

    return formula, {"t": t, "h": h, "r": r, "s": s, "n": n}


if __name__ == "__main__":
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    formula, outputs = create_model({})

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
