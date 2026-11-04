# session1_five_floors: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Run it (after `pip install mip numpy`) with:
#   python session1_five_floors.py

import mip


def create_model(instance):
    """Baker, Cooper, Fletcher, Miller and Smith live on different floors of a
    five-floor apartment house. Find the floor of each from the clues."""
    # The puzzle has no instance data: the clues are the problem statement.

    people = ["B", "C", "F", "M", "S"]  # Baker, Cooper, Fletcher, Miller, Smith
    floors = [1, 2, 3, 4, 5]  # the floors, from the first to the fifth
    low, high = floors[0], floors[-1]
    # Larger than any difference between two floors, so a rule that uses it can be switched off.
    far = (high - low) + 2

    model = mip.Model(solver_name="CBC")

    # on[p, f] is 1 when person p lives on floor f, and 0 when not.
    on = {}
    for p in people:
        for f in floors:
            on[p, f] = model.add_var(f"on_{p}_{f}", var_type=mip.BINARY)

    # floor[p] is the floor where person p lives. Baker is not on the fifth floor,
    # Cooper is not on the first, and Fletcher is on neither the first nor the fifth.
    floor = {
        "B": model.add_var("floor_B", lb=low, ub=high - 1, var_type=mip.INTEGER),
        "C": model.add_var("floor_C", lb=low + 1, ub=high, var_type=mip.INTEGER),
        "F": model.add_var("floor_F", lb=low + 1, ub=high - 1, var_type=mip.INTEGER),
        "M": model.add_var("floor_M", lb=low, ub=high, var_type=mip.INTEGER),
        "S": model.add_var("floor_S", lb=low, ub=high, var_type=mip.INTEGER),
    }

    # Each person lives on exactly one floor, and that is floor[p].
    for p in people:
        model += mip.xsum(on[p, f] for f in floors) == 1
        model += floor[p] == mip.xsum(f * on[p, f] for f in floors)

    # Each floor holds exactly one person.
    for f in floors:
        model += mip.xsum(on[p, f] for p in people) == 1

    # Miller lives on a higher floor than Cooper.
    model += floor["M"] >= floor["C"] + 1

    # Smith does not live on a floor next to Fletcher's, so they are at least two floors apart.
    # smith_below_fletcher is 1 when Smith is below Fletcher, and 0 when Smith is above.
    smith_below_fletcher = model.add_var("smith_below_fletcher", var_type=mip.BINARY)
    model += floor["S"] - floor["F"] <= -2 + far * (1 - smith_below_fletcher)
    model += floor["S"] - floor["F"] >= 2 - far * smith_below_fletcher

    # Fletcher does not live on a floor next to Cooper's, so they are at least two floors apart.
    # fletcher_below_cooper is 1 when Fletcher is below Cooper, and 0 when Fletcher is above.
    fletcher_below_cooper = model.add_var("fletcher_below_cooper", var_type=mip.BINARY)
    model += floor["F"] - floor["C"] <= -2 + far * (1 - fletcher_below_cooper)
    model += floor["F"] - floor["C"] >= 2 - far * fletcher_below_cooper

    # No objective: any arrangement of floors that meets the clues answers the puzzle.
    return model, {
        "B": floor["B"],
        "C": floor["C"],
        "F": floor["F"],
        "M": floor["M"],
        "S": floor["S"],
    }


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
