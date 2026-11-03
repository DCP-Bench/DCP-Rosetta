"""Cell towers: build towers within the budget so that the population in covered regions is as large as possible."""
import hexaly.optimizer as hx


def build(instance):
    # delta[t][r] = 1 if a tower at site t covers region r (0 if not); cost[t] = price of building a tower at site t
    delta, cost = instance["delta"], instance["cost"]
    # population[r] = inhabitants of region r; budget = most that may be spent on towers in total
    population, budget = instance["population"], instance["budget"]
    sites, regions = len(cost), len(population)  # number of candidate tower locations, number of regions
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # build_tower[t] = 1 if a cell tower is built at site t
    build_tower = [model.bool() for _ in range(sites)]
    # covered[r] = 1 if region r is counted as covered, so its population gets signal
    covered = [model.bool() for _ in range(regions)]

    # Due to budget constraints, the total cost of the towers built stays within the budget
    model.constraint(model.sum(cost[t] * build_tower[t] for t in range(sites)) <= budget)
    # A region counts as covered only if some tower built covers it. covered[r] is only bounded above;
    # the objective pushes it to 1 whenever the region can be covered
    for r in range(regions):
        model.constraint(covered[r] <= model.sum(build_tower[t] for t in range(sites) if delta[t][r]))

    # Maximise the population covered: the total number of inhabitants of the covered regions
    total_population_covered = model.sum(population[r] * covered[r] for r in range(regions))
    model.maximize(total_population_covered)
    return optimizer, {"build_tower": build_tower, "total_population_covered": total_population_covered}
