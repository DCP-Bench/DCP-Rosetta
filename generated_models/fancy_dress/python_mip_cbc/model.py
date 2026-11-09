# fancy_dress: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Run it (after `pip install mip numpy`) with:
#   python fancy_dress.py

import mip


def create_model(instance):
    """Mr Greenguest chooses which green items to wear to Mr Greenfan's party, and pays the
    $11 entrance fee if he is not dressed according to rules 1-3, at the lowest total cost.
    He owns a green shirt; a green tie costs $10, a used green hat $2, green socks $12."""
    # The instance has no fields: every number below is from the problem statement.
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    tie = model.add_var("t", var_type=mip.BINARY)    # 1 when he wears a green tie
    hat = model.add_var("h", var_type=mip.BINARY)    # 1 when he wears a green hat
    shirt = model.add_var("r", var_type=mip.BINARY)  # 1 when he wears a green shirt
    socks = model.add_var("s", var_type=mip.BINARY)  # 1 when he wears green socks
    fee = model.add_var("n", var_type=mip.BINARY)    # 1 when he pays the entrance fee

    # Rule 4: a guest who is not dressed according to rules 1-3 must pay the fee. Each rule
    # below is written as "what it asks for, or the fee": a row  item <= wanted + fee  says
    # that wearing the item needs one of the wanted items, unless he pays.

    # Rule 1: if someone wears a green tie he has to wear a green shirt.
    model += tie <= shirt + fee

    # Rule 2: a guest who wears green socks or a green shirt must also wear a green tie or
    # a green hat: the socks need a tie or a hat, and so does the shirt.
    model += socks <= tie + hat + fee
    model += shirt <= tie + hat + fee

    # Rule 3: a guest wearing a green shirt or a green hat or who does not wear green socks
    # must wear a green tie: the shirt, the hat and bare feet (1 - socks) each need the tie.
    model += shirt <= tie + fee
    model += hat <= tie + fee
    model += 1 - socks <= tie + fee

    # Minimise the total cost: the tie, the hat, the socks and the fee (the shirt he owns).
    model.objective = 10 * tie + 2 * hat + 12 * socks + 11 * fee

    return model, {"t": tie, "h": hat, "r": shirt, "s": socks, "n": fee}


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
