"""Every set of 3 distinct numbers from 1..6 whose sum is 10, with a proof that none is missing."""
import hexaly.optimizer as hx

S = hx.HxSolutionStatus
N, K, TOTAL = 6, 3, 10

with hx.HexalyOptimizer() as optimizer:
    param = optimizer.param
    param.verbosity = 0
    param.nb_threads = 4      # the bounding that proves the last step runs beside the local search
    param.set_gap_limit(0)    # OPTIMAL must mean the bound is reached exactly
    param.time_limit = 10     # per solve call
    model = optimizer.model
    pick = [model.bool() for _ in range(N)]  # pick[i]: the number i + 1 is in the set

    # Exactly K numbers, summing to TOTAL
    model.constraint(model.sum(pick) == K)
    model.constraint(model.sum((i + 1) * pick[i] for i in range(N)) == TOTAL)

    # Soft no-goods: the objective counts how many earlier solutions the decisions repeat.
    # Objective 0 is a new solution; a proven minimum of 1 or more means none is left.
    repeats = []
    model.minimize(0)
    model.close()
    solutions, complete = [], False
    while True:
        optimizer.solve()
        status = optimizer.solution.status
        if status == S.INCONSISTENT:
            complete = True
            break
        if status not in (S.FEASIBLE, S.OPTIMAL):
            break  # time limit with nothing found: not a proof
        if model.get_objective(0).value >= 1:
            complete = status == S.OPTIMAL  # minimum proven >= 1: no unseen solution exists
            break
        values = [x.value for x in pick]
        solutions.append([i + 1 for i in range(N) if values[i]])
        model.open()
        model.remove_objective(0)
        repeats.append(model.and_(*[x == v for x, v in zip(pick, values)]))
        model.minimize(model.sum(repeats))
        model.close()

    for s in sorted(solutions):
        print(s)
    print("Solutions:", len(solutions))
    print("Complete:", complete)
