# resource_constrained_project_scheduling: a PySAT (Python) model from DCP Rosetta.
# Download the `resource_constrained_project_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python resource_constrained_project_scheduling.py resource_constrained_project_scheduling.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def create_model(instance):
    """Give each job a start time so that every job starts after its predecessors have
    finished, the jobs running at any moment use no more of each resource than is
    available, and the project finishes as early as possible."""
    durations = instance["durations_data"]              # durations[j]: how long job j runs
    needs = instance["resource_needs_data"]             # needs[j][r]: units of resource r that job j uses while it runs
    capacities = instance["resource_capacities_data"]   # capacities[r]: units of resource r available at every moment
    links = instance["successors_link_data"]            # [a, b]: job b starts only after job a has finished
    n_jobs = len(durations)  # the number of jobs
    jobs = range(n_jobs)

    # Running the jobs one after another always fits, so no job needs to start after the total duration.
    horizon = sum(durations)
    # Moments at which a job may still be running: up to the horizon plus the longest job.
    times = range(horizon + max(durations + [0]))

    # Every variable of the model comes from this pool.
    pool = IDPool()

    # start[j]: the moment job j starts
    start = [Integer(f"start_time_{j}", 0, horizon, encoding="coupled", vpool=pool) for j in jobs]
    # makespan: the latest start time of any job. The last job takes no time and follows all
    # others, so this is when the project ends.
    makespan = Integer("makespan", 0, horizon, encoding="order", vpool=pool)
    engine = IntegerEngine(vars=start + [makespan], vpool=pool)

    # The constraints, and the cost of the makespan.
    formula = WCNF()
    # Each start time and the makespan is a whole number in its range.
    formula.extend(engine.clausify().clauses)

    # Whether job j starts at or after moment t.
    def at_least(j, t):
        # Before moment 0 every start qualifies, and past the horizon none does.
        if t <= 0:
            return True
        if t > horizon:
            return False
        return start[j].ge(t)

    # Adds the constraint that then holds whenever cond does. Either side may be a fixed True or False.
    def implies(cond, then):
        # Nothing to add when cond never holds or then always holds.
        if cond is False or then is True:
            return
        alternatives = [] if cond is True else [-cond]
        if then is not False:
            alternatives.append(then)
        formula.append(alternatives)

    # Precedence: job b starts only after job a has finished.
    for a, b in links:
        for t in range(0, horizon + 1):
            implies(at_least(a, t), at_least(b, t + durations[a]))

    # running[j, t] is true whenever job j is in progress at moment t, that is, it has started
    # by t and has not finished by t. Only this direction is needed: the resource limits below
    # cap the number of running jobs from above.
    running = {}
    for j in jobs:
        d = durations[j]
        if d <= 0:
            continue
        for t in times:
            # Job j is not finished before moment t.
            not_done = at_least(j, t - d + 1)
            # Job j has not started by moment t.
            not_begun = at_least(j, t + 1)
            if not_done is False or not_begun is True:
                continue
            lit = pool.id(("running", j, t))
            running[j, t] = lit
            clause = [lit]
            if not_done is not True:
                clause.append(-not_done)
            if not_begun is not False:
                clause.append(not_begun)
            formula.append(clause)

    # Resource limits: at every moment, the jobs in progress need no more units of each resource
    # than its capacity.
    for r, cap in enumerate(capacities):
        for t in times:
            # the running flags of the jobs that use resource r at moment t, with the units each uses
            lits, weights = [], []
            for j in jobs:
                if (j, t) in running and needs[j][r] > 0:
                    lits.append(running[j, t])
                    weights.append(needs[j][r])
            if sum(weights) <= cap:
                continue
            # A negative capacity cannot be met.
            if cap < 0:
                formula.append([])
                continue
            # A job that needs more units than the capacity cannot run at all.
            for lit, w in zip(lits, weights):
                if w > cap:
                    formula.append([-lit])
            formula.extend(PBEnc.leq(lits=lits, weights=weights, bound=cap, vpool=pool).clauses)

    # The makespan is at least the start time of every job.
    for j in jobs:
        for t in range(1, horizon + 1):
            formula.append([-start[j].ge(t), makespan.ge(t)])

    # Each moment up to the horizon that the makespan reaches costs 1, so a schedule pays for its latest start time.
    for t in range(1, horizon + 1):
        formula.append([-makespan.ge(t)], weight=1)

    return formula, {"start_time": start}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
