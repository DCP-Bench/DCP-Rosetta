"""Production planning: whole batches of two products, maximise profit under machine and labour hours."""
import hexaly.optimizer as hx

PROFIT = {"A": 40, "B": 30}
MACHINE = {"A": 2, "B": 1}  # hours per batch
LABOUR = {"A": 1, "B": 2}
MACHINE_HOURS, LABOUR_HOURS = 100, 80

with hx.HexalyOptimizer() as optimizer:
    optimizer.param.verbosity = 0
    optimizer.param.nb_threads = 4
    optimizer.param.set_gap_limit(0)
    optimizer.param.time_limit = 10
    model = optimizer.model
    batches = {p: model.int(0, 100) for p in PROFIT}

    # Machine and labour capacities
    model.constraint(model.sum(MACHINE[p] * batches[p] for p in PROFIT) <= MACHINE_HOURS)
    model.constraint(model.sum(LABOUR[p] * batches[p] for p in PROFIT) <= LABOUR_HOURS)

    profit = model.sum(PROFIT[p] * batches[p] for p in PROFIT)
    model.maximize(profit)
    model.close()
    optimizer.solve()

    solution = optimizer.solution
    print("Status:", solution.status.name)  # OPTIMAL: proven; FEASIBLE: best found, not proven
    if solution.status in (hx.HxSolutionStatus.FEASIBLE, hx.HxSolutionStatus.OPTIMAL):
        print("Profit:", profit.value, "bound:", solution.get_objective_bound(0))
        print({p: v.value for p, v in batches.items()})
