"""Cell towers: build towers within the budget so that the population in covered regions is as large as possible."""
import hexaly.optimizer as hx


def build(instance):
    delta, cost = instance["delta"], instance["cost"]  # delta[t][r] = 1 if a tower at site t covers region r
    population, budget = instance["population"], instance["budget"]
    sites, regions = len(cost), len(population)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    build_tower = [model.bool() for _ in range(sites)]
    covered = [model.bool() for _ in range(regions)]

    # The towers built stay within the budget
    model.constraint(model.sum(cost[t] * build_tower[t] for t in range(sites)) <= budget)
    # A region counts as covered only if some tower built covers it
    for r in range(regions):
        model.constraint(covered[r] <= model.sum(build_tower[t] for t in range(sites) if delta[t][r]))

    # Maximise the population of the covered regions
    total_population_covered = model.sum(population[r] * covered[r] for r in range(regions))
    model.maximize(total_population_covered)
    return optimizer, {"build_tower": build_tower, "total_population_covered": total_population_covered}
