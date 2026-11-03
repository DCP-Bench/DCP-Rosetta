# cell_tower: a SCIP (Python) model from DCP Rosetta.
# Download the `cell_tower.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python cell_tower.py cell_tower.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """A telecom company chooses which candidate cell tower sites to build, within
    its budget, so that the population living in covered regions is as large as
    possible. A region is covered when at least one built tower reaches it."""
    cost = np.array(instance["cost"])              # cost[j]: the price of a tower at site j
    reach = np.array(instance["delta"])            # reach[j][i] is 1 when a tower at site j covers region i, else 0
    population = np.array(instance["population"])  # population[i]: the inhabitants of region i
    budget = instance["budget"]                    # the most money the company can spend on towers

    n_sites = len(cost)
    n_regions = len(population)

    model = Model("cell_tower")

    # build[j] is 1 when a tower is built at site j, and 0 when not
    build = model.addMatrixVar(n_sites, vtype="B", name="build")
    # covered[i] is 1 when region i is covered; it can only be 1 when a built tower
    # reaches region i, and the maximisation sets it to 1 wherever it can
    covered = model.addMatrixVar(n_regions, vtype="B", name="covered")
    # total is the population covered; it equals the sum over covered regions.
    # lb=0 is an assumption: populations are head counts, so none is negative.
    # ub is the whole population, the most that can be covered.
    total = model.addVar(name="total", vtype="I", lb=0, ub=int(population.sum()))

    # Region i can be covered only if at least one built tower reaches it.
    model.addMatrixCons(covered <= build @ reach)

    # The towers built cost no more than the budget.
    model.addCons((build * cost).sum() <= budget)

    # The total is the population of the covered regions.
    model.addCons(total == (covered * population).sum())

    # Cover as many inhabitants as possible.
    model.setObjective(total, "maximize")

    return model, {"build_tower": build, "total_population_covered": total}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
