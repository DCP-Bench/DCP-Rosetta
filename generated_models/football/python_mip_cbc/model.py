# football: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
# Run it (after `pip install mip numpy`) with:
#   python football.py

import mip


def create_model(instance):
    """Choose football players from four groups to spend as much money as possible without going
    over GBP 30 million. Buy exactly one goalkeeper, at least two defenders, at least three
    midfielders and at least two strikers, and at least eleven players in all. Report the total
    price of the players bought, in GBP thousands."""
    # Prices are in GBP thousands: the price in GBP millions times 1000.
    goalkeepers = [730, 1280, 3880]  # goalkeepers g1 to g3
    defenders = [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570]  # defenders d1 to d8
    midfielders = [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130]  # midfielders m1 to m10
    strikers = [4460, 6470, 7780, 8390, 9500]  # strikers s1 to s5
    groups = [goalkeepers, defenders, midfielders, strikers]  # the four groups of players
    budget = 30000  # the chairman's limit of GBP 30 million

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # buy[k][i] is 1 when player i of group k is bought, and 0 when not.
    buy = [[model.add_var(f"buy_{k}_{i}", var_type=mip.BINARY) for i in range(len(group))]
           for k, group in enumerate(groups)]
    # The bought flags of the goalkeepers, defenders, midfielders and strikers, in turn.
    g, d, m, s = buy

    # Exactly one goalkeeper, at least two defenders, at least three midfielders and at least two strikers.
    model += mip.xsum(g) == 1
    model += mip.xsum(d) >= 2
    model += mip.xsum(m) >= 3
    model += mip.xsum(s) >= 2

    # At least eleven players in all.
    model += mip.xsum(g + d + m + s) >= 11

    # z is the total price of the players bought, in GBP thousands. It cannot exceed the budget.
    z = model.add_var("z", lb=0, ub=budget, var_type=mip.INTEGER)
    model += z == mip.xsum(price * flag for group, flags in zip(groups, buy)
                           for price, flag in zip(group, flags))

    # Spend as much as possible.
    model.objective = z

    return model, {"z": z}


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
