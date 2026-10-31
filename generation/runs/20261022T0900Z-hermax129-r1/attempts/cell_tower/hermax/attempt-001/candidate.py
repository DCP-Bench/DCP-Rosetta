from hermax.model import Model


def build(instance):
    # Read instance data
    delta = instance["delta"]  # coverage matrix: delta[site][region]
    cost = instance["cost"]  # cost for each site
    population = instance["population"]  # population in each region
    budget = instance["budget"]  # budget constraint

    num_sites = len(delta)
    num_regions = len(delta[0])

    m = Model()

    # Decision variables: whether to build a tower at each site
    build_tower = m.bool_vector("build_tower", num_sites)

    # Coverage variables: whether each region is covered
    covered = m.bool_vector("covered", num_regions)

    # Budget constraint: total cost must not exceed budget
    # sum(cost[s] * build_tower[s]) <= budget
    m &= (sum(cost[s] * build_tower[s] for s in range(num_sites)) <= budget)

    # Coverage constraints: a region is covered iff at least one tower covering it is built
    # covered[r] -> exists s: delta[s][r] == 1 and build_tower[s] == 1
    # Equivalently: if covered[r] is true, at least one covering tower must be built
    # And if covered[r] is false, no region coverage is gained
    for r in range(num_regions):
        # covered[r] can only be true if at least one site covering region r is built
        # This is: covered[r] <= sum(delta[s][r] * build_tower[s])
        coverage_sum = sum(delta[s][r] * build_tower[s] for s in range(num_sites))
        m &= (covered[r] <= coverage_sum)

    # Objective: maximize total population covered
    # Pay when region is NOT covered, so minimizing cost maximizes coverage
    for r in range(num_regions):
        m.obj[population[r]] += covered[r]

    # Output: total_population_covered as a sum of covered populations
    total_population_covered = sum(population[r] * covered[r] for r in range(num_regions))

    return m, {
        "build_tower": build_tower,
        "total_population_covered": total_population_covered
    }
