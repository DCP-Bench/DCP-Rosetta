# fancy_dress: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Run it (after `pip install exact numpy`) with:
#   python fancy_dress.py

from exact import Exact


def create_model(instance):
    """Mr Greenguest wants to attend a party where guests must wear green. He owns
    only a green shirt, and can buy a green tie, a green hat and green socks, or
    pay the entrance fee instead of following the dress rules. Find the cheapest way."""
    price_tie = 10     # a green tie costs 10
    price_hat = 2      # a green hat (used) costs 2
    price_socks = 12   # green socks cost 12
    price_fee = 11     # the entrance fee is 11

    solver = Exact()

    # Exact identifies its variables by name.
    # t is 1 when he wears a green tie, and 0 when not
    solver.addVariable("t", 0, 1)
    # h is 1 when he wears a green hat, and 0 when not
    solver.addVariable("h", 0, 1)
    # r is 1 when he wears a green shirt, and 0 when not
    solver.addVariable("r", 0, 1)
    # s is 1 when he wears green socks, and 0 when not
    solver.addVariable("s", 0, 1)
    # n is 1 when he pays the entrance fee, and 0 when not
    solver.addVariable("n", 0, 1)

    # Rule 1: a green tie needs a green shirt, unless he pays the fee.
    solver.addConstraint([(1, "r"), (1, "n"), (-1, "t")], True, 0)

    # Rule 2: green socks, or a green shirt, need a green tie or a green hat, unless he pays the fee.
    solver.addConstraint([(1, "t"), (1, "h"), (1, "n"), (-1, "s")], True, 0)
    solver.addConstraint([(1, "t"), (1, "h"), (1, "n"), (-1, "r")], True, 0)

    # Rule 3: a green shirt, a green hat, or no green socks needs a green tie, unless he pays the fee.
    solver.addConstraint([(1, "t"), (1, "n"), (-1, "r")], True, 0)
    solver.addConstraint([(1, "t"), (1, "n"), (-1, "h")], True, 0)
    solver.addConstraint([(1, "t"), (1, "n"), (1, "s")], True, 1)

    # Minimise what he spends on the tie, hat, socks and fee. The shirt is already owned, so it is not counted.
    cost = [(price_tie, "t"), (price_hat, "h"), (price_socks, "s"), (price_fee, "n")]
    solver.setObjective(cost, minimize=True)

    return solver, {"t": "t", "h": "h", "r": "r", "s": "s", "n": "n"}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
