# birthday_coins: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install mip numpy`) with:
#   python birthday_coins.py

import mip


def create_model(instance):
    """Tommy was given 15 coins for his birthday, all half-crowns, shillings and sixpences.
    Added up, they come to one pound, five shillings and six pence. Find how many half-crowns
    he was given."""
    total_coins = 15                 # the number of coins Tommy was given
    shillings_per_pound = 20         # a pound is 20 shillings
    pence_per_shilling = 12          # a shilling is 12 pence
    total_pence = (shillings_per_pound + 5) * pence_per_shilling + 6  # one pound, five shillings and six pence
    half_crown_pence = 2 * pence_per_shilling + 6  # a half-crown is two shillings and sixpence
    sixpence_pence = 6               # a sixpence is 6 pence

    model = mip.Model(solver_name="CBC")

    # the number of half-crowns Tommy was given
    half_crowns = model.add_var("half_crowns", lb=0, ub=total_coins, var_type=mip.INTEGER)
    # the number of shillings Tommy was given
    shillings = model.add_var("shillings", lb=0, ub=total_coins, var_type=mip.INTEGER)
    # the number of sixpences Tommy was given
    sixpences = model.add_var("sixpences", lb=0, ub=total_coins, var_type=mip.INTEGER)

    # The coins are 15 in all.
    model.add_constr(mip.xsum([half_crowns, shillings, sixpences]) == total_coins)

    # The coins add up to one pound, five shillings and six pence.
    model.add_constr(
        mip.xsum([half_crown_pence * half_crowns,
                  pence_per_shilling * shillings,
                  sixpence_pence * sixpences]) == total_pence
    )

    return model, {"half_crowns": half_crowns}


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
