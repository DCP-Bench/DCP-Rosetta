"""Assign 4 workers to 4 jobs, one job each, at minimum total cost.

Boolean assignment variables with linear constraints give Hexaly a bound it can close. The
same problem as a list decision (a permutation) finds cost 13 too, but stays FEASIBLE with
a bound of 4 after 10 seconds.
"""
import hexaly.optimizer as hx

COST = [[9, 2, 7, 8],
        [6, 4, 3, 7],
        [5, 8, 1, 8],
        [7, 6, 9, 4]]
N = len(COST)

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)
    optimizer.param.time_limit = 10
    model = optimizer.model
    assign = [[model.bool() for _ in range(N)] for _ in range(N)]  # assign[w][j]: worker w does job j

    # Every worker does one job, and every job is done by one worker
    for w in range(N):
        model.constraint(model.sum(assign[w]) == 1)
    for j in range(N):
        model.constraint(model.sum(assign[w][j] for w in range(N)) == 1)

    total = model.sum(COST[w][j] * assign[w][j] for w in range(N) for j in range(N))
    model.minimize(total)
    model.close()
    optimizer.solve()

    status = optimizer.solution.status
    print("Status:", status.name)
    if status in (hx.HxSolutionStatus.FEASIBLE, hx.HxSolutionStatus.OPTIMAL):
        print("Total cost:", total.value)
        print("Jobs:", [next(j for j in range(N) if assign[w][j].value) for w in range(N)])
