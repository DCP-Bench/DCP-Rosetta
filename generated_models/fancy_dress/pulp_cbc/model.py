# fancy_dress: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Run it (after `pip install pulp numpy`) with:
#   python fancy_dress.py

import pulp


def create_model(instance):
    """Mr Greenguest wants to attend a party where guests must wear green. He owns
    only a green shirt, and can buy a green tie, a green hat and green socks, or
    pay the entrance fee instead of following the dress rules. Find the cheapest way."""
    problem = pulp.LpProblem("fancy_dress", pulp.LpMinimize)

    # t is 1 when he wears a green tie, and 0 when not
    t = pulp.LpVariable("t", cat="Binary")
    # h is 1 when he wears a green hat, and 0 when not
    h = pulp.LpVariable("h", cat="Binary")
    # r is 1 when he wears a green shirt, and 0 when not
    r = pulp.LpVariable("r", cat="Binary")
    # s is 1 when he wears green socks, and 0 when not
    s = pulp.LpVariable("s", cat="Binary")
    # n is 1 when he pays the entrance fee, and 0 when not
    n = pulp.LpVariable("n", cat="Binary")

    # Unless he pays the fee, he has to follow the three dress rules.
    # Rule 1: a green tie needs a green shirt.
    problem += t <= r + n
    # Rule 2: green socks or a green shirt need a green tie or a green hat.
    problem += s <= t + h + n
    problem += r <= t + h + n
    # Rule 3: a green shirt, a green hat, or no green socks needs a green tie.
    problem += r <= t + n
    problem += h <= t + n
    problem += 1 - s <= t + n

    # The total cost is the price of the tie, hat, socks and fee. He already owns the shirt.
    problem += 10 * t + 2 * h + 12 * s + 11 * n

    return problem, {"t": t, "h": h, "r": r, "s": s, "n": n}


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
