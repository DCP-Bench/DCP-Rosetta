"""Every minimum vertex cover of a 4-cycle (0-1-2-3-0) plus an isolated vertex 4."""
import hexaly.optimizer as hx

S = hx.HxSolutionStatus
EDGES = [(0, 1), (1, 2), (2, 3), (3, 0)]
V = 5

with hx.HexalyOptimizer() as optimizer:
    param = optimizer.param
    param.verbosity = 0
    param.nb_threads = 4
    param.set_gap_limit(0)  # the default gap 1e-4 may call a non-optimal solution OPTIMAL
    param.time_limit = 10
    model = optimizer.model
    chosen = [model.bool() for _ in range(V)]

    # Every edge has at least one end in the cover
    for a, b in EDGES:
        model.constraint(chosen[a] | chosen[b])

    size = model.sum(chosen)
    model.minimize(size)
    model.close()
    optimizer.solve()
    if optimizer.solution.status != S.OPTIMAL:
        raise SystemExit(f"optimum not proven: {optimizer.solution.status.name}")
    best = size.value
    print("Minimum cover size:", best)

    # Keep only optimal assignments, then enumerate them with soft no-goods
    model.open()
    model.remove_objective(0)
    model.constraint(size == best)
    repeats = []
    model.minimize(0)
    model.close()
    covers, complete = [], False
    while True:
        optimizer.solve()
        status = optimizer.solution.status
        if status == S.INCONSISTENT:
            complete = True
            break
        if status not in (S.FEASIBLE, S.OPTIMAL):
            break
        if model.get_objective(0).value >= 1:
            complete = status == S.OPTIMAL
            break
        values = [x.value for x in chosen]
        covers.append([i for i in range(V) if values[i]])
        model.open()
        model.remove_objective(0)
        repeats.append(model.and_(*[x == v for x, v in zip(chosen, values)]))
        model.minimize(model.sum(repeats))
        model.close()

    print("Optimal covers:", len(covers), sorted(covers))
    print("Complete:", complete)
