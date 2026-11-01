# fancy_dress: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Run it (after `pip install cpmpy`) with:
#   python fancy_dress.py

import cpmpy as cp


def create_model(instance):
    """Mr Greenguest wants to attend a party where guests must wear green. He owns
    only a green shirt, and can buy a green tie, a green hat and green socks, or
    pay the entrance fee instead of following the dress rules. Find the cheapest way."""
    # t is true when he wears a green tie (costs 10)
    t = cp.boolvar(name="t")
    # h is true when he wears a green hat (costs 2)
    h = cp.boolvar(name="h")
    # r is true when he wears a green shirt (he already owns it, so it costs nothing)
    r = cp.boolvar(name="r")
    # s is true when he wears green socks (costs 12)
    s = cp.boolvar(name="s")
    # n is true when he pays the entrance fee (costs 11)
    n = cp.boolvar(name="n")
    # cost is what he pays in total; at most 10 + 2 + 12 + 11 = 35
    cost = cp.intvar(0, 35, name="cost")

    model = cp.Model()

    # Without the entrance fee, he has to follow the three dress rules.
    # Rule 1: a green tie requires a green shirt.
    model.add(t.implies(r) | n)
    # Rule 2: green socks or a green shirt require a green tie or a green hat.
    model.add((s | r).implies(t | h) | n)
    # Rule 3: a green shirt, a green hat, or no green socks requires a green tie.
    model.add((r | h | ~s).implies(t) | n)

    # The total cost is the price of each thing he wears or pays.
    model.add(cost == 10 * t + 2 * h + 12 * s + 11 * n)

    # Minimize the total cost.
    model.minimize(cost)

    return model, {"t": t, "h": h, "r": r, "s": s, "n": n}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
