# fancy_dress: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Run it (after `pip install pychoco numpy`) with:
#   python fancy_dress.py

from pychoco.model import Model


def rule(model, needed, trigger):
    """Post a dress rule: one of the items in needed is worn, or one of the items in trigger is not worn."""
    model.scalar(needed + trigger, [1] * len(needed) + [-1] * len(trigger), ">=", 1 - len(trigger)).post()


def create_model(instance):
    """Mr Greenguest wants to attend a party where guests must wear green. He owns
    only a green shirt, and can buy a green tie, a green hat and green socks, or
    pay the entrance fee instead of following the dress rules. Find the cheapest way."""
    model = Model()

    # t is true when he wears a green tie
    t = model.boolvar(name="t")
    # h is true when he wears a green hat
    h = model.boolvar(name="h")
    # r is true when he wears his green shirt, which he already owns
    r = model.boolvar(name="r")
    # s is true when he wears green socks
    s = model.boolvar(name="s")
    # n is true when he pays the entrance fee instead of following the rules
    n = model.boolvar(name="n")

    # The dress rules. Each one holds unless he pays the entrance fee.
    # A green tie needs a green shirt.
    rule(model, [r, n], [t])
    # Green socks or a green shirt need a green tie or a green hat.
    rule(model, [t, h, n], [s])
    rule(model, [t, h, n], [r])
    # A green shirt, a green hat or no green socks need a green tie.
    rule(model, [t, n], [r])
    rule(model, [t, n], [h])
    rule(model, [s, t, n], [])

    # Prices of the green tie, the green hat, the green socks and the entrance fee.
    prices = [10, 2, 12, 11]

    # The total he pays. The shirt is already owned, so it costs nothing.
    cost = model.intvar(0, sum(prices), name="cost")
    model.scalar([t, h, s, n], prices, "=", cost).post()

    return model, {"t": t, "h": h, "r": r, "s": s, "n": n}, {"objective": cost, "maximize": False}


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
