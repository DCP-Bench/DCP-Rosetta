# ages_of_the_sons: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Run it (after `pip install mip numpy`) with:
#   python ages_of_the_sons.py

import mip


def create_model(instance):
    """An old man's three sons have ages with product 36. Learning the sum of
    their ages does not settle them, but learning that the oldest son is unique
    does. Find the ages, oldest first."""
    product = 36
    # Every set of three positive ages with product 36, listed oldest first.
    triples = []
    for a in range(1, product + 1):
        for b in range(1, a + 1):
            for c in range(1, b + 1):
                if a * b * c == product:
                    triples.append((a, b, c))
    max_age = max(max(t) for t in triples)
    max_sum = max(sum(t) for t in triples)

    model = mip.Model(solver_name="CBC")

    # pick[k] is 1 when the sons' ages are triples[k].
    pick = [model.add_var(f"pick_{k}", var_type=mip.BINARY) for k in range(len(triples))]
    # The sons' ages are exactly one of the triples.
    model.add_constr(mip.xsum(pick) == 1)

    # The ages of the three sons, oldest first.
    ages = [model.add_var(f"A{i + 1}", lb=1, ub=max_age, var_type=mip.INTEGER) for i in range(3)]
    # Each son's age is the matching age of the chosen triple.
    for i in range(3):
        model.add_constr(ages[i] == mip.xsum(t[i] * pick[k] for k, t in enumerate(triples)))

    # The number of windows in the building. It is the sum of the sons' ages, and is at most the largest possible sum.
    windows = model.add_var("windows", lb=3, ub=max_sum, var_type=mip.INTEGER)
    model.add_constr(windows == ages[0] + ages[1] + ages[2])

    # same_sum[k] is 1 when triple k has the same sum as the windows count.
    same_sum = [model.add_var(f"same_sum_{k}", var_type=mip.BINARY) for k in range(len(triples))]
    for k, t in enumerate(triples):
        model.add_constr(windows - sum(t) <= max_sum * (1 - same_sum[k]))
        model.add_constr(sum(t) - windows <= max_sum * (1 - same_sum[k]))
    # Two or more triples share that sum, so the sum alone does not settle the ages.
    model.add_constr(mip.xsum(same_sum) >= 2)

    # The oldest son is unique, so he is older than the second son.
    model.add_constr(ages[0] >= ages[1] + 1)

    return model, {"A1": ages[0], "A2": ages[1], "A3": ages[2]}


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
