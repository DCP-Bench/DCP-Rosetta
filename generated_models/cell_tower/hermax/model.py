# cell_tower: a hermax (Python) model from DCP Rosetta.
# Download the `cell_tower.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cell_tower.html
# Then run it on the first instance (after `pip install hermax`):
#   python cell_tower.py cell_tower.json

import functools
import operator

from hermax.model import Model, sum_expr


def create_model(instance):
    """Choose which candidate cell towers to build, without spending more than the budget,
    so that the total population covered by at least one built tower is as large as possible.

    A region counts as covered only when at least one tower that reaches it is built."""
    delta = instance["delta"]            # delta[s][r] = 1 when a tower at site s reaches region r
    cost = instance["cost"]              # cost[s]: the price of building a tower at site s
    population = instance["population"]  # population[r]: the inhabitants of region r
    budget = instance["budget"]          # the most money that may be spent on towers

    num_sites = len(cost)          # the number of candidate tower sites
    num_regions = len(population)  # the number of regions

    m = Model()

    # build_tower[s] is true when a tower is built at site s
    build_tower = m.bool_vector("build_tower", num_sites)
    # covered[r] may be true only when region r has signal (the objective makes it true whenever possible)
    covered = m.bool_vector("covered", num_regions)

    # The towers built cost no more than the budget.
    m &= (sum(cost[s] * build_tower[s] for s in range(num_sites)) <= budget)

    # A region can be covered only if at least one tower that reaches it is built.
    for r in range(num_regions):
        # the literals of the sites whose towers reach region r
        reaching = [build_tower[s] for s in range(num_sites) if delta[s][r] == 1]
        # "not covered, or one of the reaching towers is built" as one clause
        m &= functools.reduce(operator.or_, reaching, ~covered[r])

    # Minimise the population left without signal, which maximises the population covered.
    m.obj += sum(population[r] * ~covered[r] for r in range(num_regions))

    # The total population covered: the populations of the covered regions added up.
    total_population_covered = sum_expr(population[r] * covered[r] for r in range(num_regions))

    # The objective in the problem's terms: the total population covered; the solver minimises
    # the population left uncovered, its complement to the whole population.
    return m, {
        "build_tower": build_tower,
        "total_population_covered": total_population_covered,
    }, total_population_covered


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
