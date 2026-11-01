# fancy_dress: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Run it (after `pip install ortools`) with:
#   python fancy_dress.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Mr Greenguest wants to attend a party where guests must wear green. He owns
    only a green shirt, and can buy a green tie, a green hat and green socks, or
    pay the entrance fee instead of following the dress rules. Find the cheapest way."""
    model = cp_model.CpModel()

    # tie is true when he wears a green tie (costs 10)
    tie = model.new_bool_var("tie")
    # hat is true when he wears a green hat (costs 2)
    hat = model.new_bool_var("hat")
    # shirt is true when he wears a green shirt (he owns it, so it costs nothing)
    shirt = model.new_bool_var("shirt")
    # socks is true when he wears green socks (costs 12)
    socks = model.new_bool_var("socks")
    # fee is true when he pays the entrance fee (costs 11)
    fee = model.new_bool_var("fee")

    # Without paying the fee, he has to follow the three dress rules.
    # Rule 1: a green tie needs a green shirt.
    model.add_bool_or([~tie, shirt, fee])
    # Rule 2: green socks, or a green shirt, need a green tie or a green hat.
    model.add_bool_or([~socks, tie, hat, fee])
    model.add_bool_or([~shirt, tie, hat, fee])
    # Rule 3: a green shirt, a green hat, or no green socks needs a green tie.
    model.add_bool_or([~shirt, tie, fee])
    model.add_bool_or([~hat, tie, fee])
    model.add_bool_or([socks, tie, fee])

    # The total cost is the price of the tie, hat, socks and fee. The shirt is free.
    cost = model.new_int_var(0, 35, "cost")
    model.add(cost == 10 * tie + 2 * hat + 12 * socks + 11 * fee)

    # Minimize the total cost.
    model.minimize(cost)

    return model, {"t": tie, "h": hat, "r": shirt, "s": socks, "n": fee}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
