# fancy_dress: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Run it (after `pip install z3-solver numpy`) with:
#   python fancy_dress.py

import z3


def create_model(instance):
    """Mr Greenguest wants to attend a dress party where the guests must wear green. He owns
    a green shirt already, and can buy a green tie, a green hat and green socks, or pay the
    entrance fee instead of following the dress rules. Find the cheapest way to attend."""
    # t is true when he wears a green tie
    t = z3.Bool("t")
    # h is true when he wears a green hat
    h = z3.Bool("h")
    # r is true when he wears a green shirt
    r = z3.Bool("r")
    # s is true when he wears green socks
    s = z3.Bool("s")
    # n is true when he pays the entrance fee
    n = z3.Bool("n")

    solver = z3.Optimize()

    solver.add(
        # Rule 1: a green tie requires a green shirt.
        z3.Or(z3.Implies(t, r), n),
        # Rule 2: green socks or a green shirt are only allowed together with a green tie or a green hat.
        z3.Or(z3.Implies(z3.Or(s, r), z3.Or(t, h)), n),
        # Rule 3: a green shirt, a green hat, or socks that are not green require a green tie.
        z3.Or(z3.Implies(z3.Or(r, h, z3.Not(s)), t), n),
    )

    # Prices: tie $10, hat $2, socks $12, entrance fee $11. He owns the shirt, so it costs nothing.
    cost = z3.If(t, 10, 0) + z3.If(h, 2, 0) + z3.If(s, 12, 0) + z3.If(n, 11, 0)

    # Minimize the total cost.
    solver.minimize(cost)

    return solver, {"t": t, "h": h, "r": r, "s": s, "n": n}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
