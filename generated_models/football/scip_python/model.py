# football: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python football.py

from pyscipopt import Model, quicksum

# The players available and their prices in GBP thousands. The statement gives the prices in
# GBP millions with at most three decimals, so 0.73 million is 730 thousand and 3.769 million is
# 3769 thousand: every price is an integer.
GOALKEEPERS = [("g1", 730), ("g2", 1280), ("g3", 3880)]
DEFENDERS = [("d1", 920), ("d2", 1310), ("d3", 1620), ("d4", 2410),
             ("d5", 2790), ("d6", 3280), ("d7", 3910), ("d8", 4570)]
MIDFIELDERS = [("m1", 1800), ("m2", 2630), ("m3", 3170), ("m4", 3769), ("m5", 4140),
               ("m6", 4750), ("m7", 5380), ("m8", 5930), ("m9", 6780), ("m10", 7130)]
STRIKERS = [("s1", 4460), ("s2", 6470), ("s3", 7780), ("s4", 8390), ("s5", 9500)]

# The chairman's upper limit of GBP 30 million, in GBP thousands.
BUDGET = 30000


def create_model(instance):
    """Choose a football squad from the players available: the total price should be as high as
    possible without going over the budget, and the squad must include the required numbers of
    goalkeepers, defenders, midfielders and strikers. The output z is the total price of the
    squad in GBP thousands. The instance file is empty ([]), so every price, count and the budget
    come from the problem statement and the model reads nothing from its argument."""
    model = Model("football")

    def choose(group):
        # one binary per player, named x_<player>: 1 when the player is bought, 0 when not
        return [model.addVar(f"x_{name}", vtype="B") for name, _ in group]

    goalkeepers = choose(GOALKEEPERS)
    defenders = choose(DEFENDERS)
    midfielders = choose(MIDFIELDERS)
    strikers = choose(STRIKERS)
    players = GOALKEEPERS + DEFENDERS + MIDFIELDERS + STRIKERS
    bought = goalkeepers + defenders + midfielders + strikers  # bought[i] belongs to players[i]

    # Exactly one goalkeeper must be bought.
    model.addCons(quicksum(goalkeepers) == 1)
    # At least two defenders must be bought.
    model.addCons(quicksum(defenders) >= 2)
    # At least three midfielders must be bought.
    model.addCons(quicksum(midfielders) >= 3)
    # At least two strikers must be bought.
    model.addCons(quicksum(strikers) >= 2)
    # At least eleven players must be bought in total.
    model.addCons(quicksum(bought) >= 11)

    # z is the total price of the squad in GBP thousands. Its upper bound is the chairman's
    # budget, so the squad never costs more than that limit.
    z = model.addVar("z", vtype="I", lb=0, ub=BUDGET)
    # z is the sum of the prices of the players bought.
    model.addCons(z == quicksum(price * x for (_, price), x in zip(players, bought)))

    # Maximise the total price: the statement wants the purchases as close to the budget as possible.
    model.setObjective(z, "maximize")

    return model, {"z": z}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
