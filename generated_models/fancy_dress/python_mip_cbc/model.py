# fancy_dress: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Run it (after `pip install mip numpy`) with:
#   python fancy_dress.py

import mip


def create_model(instance):
    """Mr Greenguest wants to attend a party where guests must wear green. He owns
    only a green shirt and can buy a green tie, a green hat and green socks, or pay
    the entrance fee instead of following the dress rules. Find the cheapest way."""
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # tie is true when he wears a green tie (costs 10)
    tie = model.add_var("tie", var_type=mip.BINARY)
    # hat is true when he wears a green hat (costs 2)
    hat = model.add_var("hat", var_type=mip.BINARY)
    # shirt is true when he wears a green shirt (he owns it, so it costs nothing)
    shirt = model.add_var("shirt", var_type=mip.BINARY)
    # socks is true when he wears green socks (costs 12)
    socks = model.add_var("socks", var_type=mip.BINARY)
    # fee is true when he pays the entrance fee (costs 11)
    fee = model.add_var("fee", var_type=mip.BINARY)

    # Breaking a dress rule means paying the fee, so fee is true whenever a rule below is broken.
    # Rule 1: a green tie needs a green shirt.
    model += fee >= tie - shirt
    # Rule 2: green socks together with a green shirt need a green tie or a green hat.
    model += fee >= socks + shirt - tie - hat - 1
    # Rule 3: a green shirt, a green hat, or no green socks needs a green tie.
    model += fee >= shirt - tie
    model += fee >= hat - tie
    model += fee >= 1 - socks - tie

    # Minimize the total cost of the tie, hat, socks and fee.
    model.objective = 10 * tie + 2 * hat + 12 * socks + 11 * fee

    return model, {"h": hat, "n": fee, "r": shirt, "s": socks, "t": tie}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
