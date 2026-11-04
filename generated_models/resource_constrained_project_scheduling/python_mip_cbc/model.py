# resource_constrained_project_scheduling: a Python-MIP (Python) model from DCP Rosetta.
# Download the `resource_constrained_project_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python resource_constrained_project_scheduling.py resource_constrained_project_scheduling.json

import mip


# Place the jobs one after another in the given order. Each job starts at the earliest
# time after its predecessors have finished at which no resource goes over its capacity.
def _serial_schedule(order, dur, need, cap, preds, n_periods):
    n_jobs = len(dur)
    used = [[0] * len(cap) for _ in range(n_periods)]  # units of each resource in use at each time
    start = [0] * n_jobs   # start time of each job
    finish = [0] * n_jobs  # finish time of each job
    for j in order:
        t = max([finish[p] for p in preds[j]], default=0)
        while not _fits_at(used, t, dur[j], need[j], cap):
            t += 1
        _occupy(used, t, dur[j], need[j])
        start[j] = t
        finish[j] = t + dur[j]
    return start, max(finish, default=0)


# Add the units of a job that runs from time t for its duration to the use of each resource.
def _occupy(used, t, duration, need):
    for time in range(t, t + duration):
        for k, units in enumerate(need):
            used[time][k] += units


# True when a job with the given duration and needs can run from time t without any
# resource going over its capacity.
def _fits_at(used, t, duration, need, cap):
    for time in range(t, t + duration):
        for k, units in enumerate(need):
            if used[time][k] + units > cap[k]:
                return False
    return True


# Backward pass: place the jobs from the last one to the first, each as late as its successors
# and the makespan allow. Returns the latest start time of each job, or None when a job does
# not fit at any time from 0 on.
def _backward_pass(start, makespan, dur, need, cap, succs, n_periods):
    n_jobs = len(dur)
    used = [[0] * len(cap) for _ in range(n_periods)]  # the same as in the serial schedule, for the jobs placed here
    late = [None] * n_jobs  # latest start time of each job, None until it is placed
    unplaced = set(range(n_jobs))
    while unplaced:
        ready = [j for j in unplaced if all(late[s] is not None for s in succs[j])]
        j = max(ready, key=lambda i: (start[i] + dur[i], start[i], i))
        t = min([late[s] for s in succs[j]], default=makespan) - dur[j]
        while t >= 0 and not _fits_at(used, t, dur[j], need[j], cap):
            t -= 1
        if t < 0:
            return None
        _occupy(used, t, dur[j], need[j])
        late[j] = t
        unplaced.discard(j)
    return late


# An upper bound on the makespan, from a schedule found by a fixed local search with no
# randomness. The schedules are improved by backward and forward passes, and then by moving
# one job to another place in the order.
def _heuristic_makespan(dur, need, cap, preds, succs, pairs, tail, n_periods):
    n_jobs = len(dur)

    # True when every job comes after its predecessors in the order.
    def is_precedence_order(order):
        return all(order.index(a) < order.index(b) for a, b in pairs)

    # Makespan of the serial schedule of the order, improved by backward and forward passes
    # for as long as that shortens it.
    def evaluate(order):
        start, makespan = _serial_schedule(order, dur, need, cap, preds, n_periods)
        while True:
            rank = {j: idx for idx, j in enumerate(order)}  # position of each job in the order
            late = _backward_pass(start, makespan, dur, need, cap, succs, n_periods)
            if late is None:
                break
            new_order = sorted(range(n_jobs), key=lambda j: (late[j], rank[j]))
            start2, makespan2 = _serial_schedule(new_order, dur, need, cap, preds, n_periods)
            if makespan2 >= makespan:
                break
            start, makespan = start2, makespan2
            order = new_order
        return makespan

    # Build the order one job at a time. Among the jobs whose predecessors are all placed,
    # the one with the longest tail goes first, and the lower index breaks ties.
    waiting = [len(preds[j]) for j in range(n_jobs)]  # predecessors of each job not yet in the order
    ready = [j for j in range(n_jobs) if waiting[j] == 0]  # jobs that may come next in the order
    order = []  # the order built so far
    while ready:
        j = max(ready, key=lambda i: (tail[i], -i))
        ready.remove(j)
        order.append(j)
        for s in succs[j]:
            waiting[s] -= 1
            if waiting[s] == 0:
                ready.append(s)

    best = evaluate(order)
    # Move one job to another place in the order and keep the first move that shortens the
    # schedule. Repeat until no move does.
    while True:
        moved = False
        for p in range(n_jobs):
            for q in range(n_jobs):
                if p == q:
                    continue
                candidate = list(order)
                job = candidate.pop(p)
                candidate.insert(q, job)
                if not is_precedence_order(candidate):
                    continue
                makespan = evaluate(candidate)
                if makespan < best:
                    order, best = candidate, makespan
                    moved = True
                    break
            if moved:
                break
        if not moved:
            break
    return best


def create_model(instance):
    """Schedule jobs with given durations and resource needs so that every precedence
    holds and no resource is used beyond its capacity at any time, with the project
    finishing as early as possible."""
    dur = instance["durations_data"]            # dur[j]: how long job j takes
    need = instance["resource_needs_data"]      # need[j][k]: units of resource k that job j uses while it runs
    cap = instance["resource_capacities_data"]  # cap[k]: units of resource k available at any time
    succ = instance["successors_link_data"]     # [a, b]: job b can start only once job a has finished
    n_jobs = len(dur)                           # number of jobs

    preds = [[] for _ in range(n_jobs)]  # preds[j]: the jobs that must finish before job j starts
    succs = [[] for _ in range(n_jobs)]  # succs[j]: the jobs that wait for job j to finish
    for a, b in succ:
        preds[b].append(a)
        succs[a].append(b)

    # tail[j]: the longest chain of durations from job j to the end of the project, job j included
    tail = list(dur)
    for _ in range(n_jobs):
        for a, b in succ:
            tail[a] = max(tail[a], dur[a] + tail[b])
    # head[j]: the earliest time job j can start, given the precedences alone
    head = [0] * n_jobs
    for _ in range(n_jobs):
        for a, b in succ:
            head[b] = max(head[b], head[a] + dur[a])

    # Lower bound on the makespan: the longest chain of precedences, and for each resource the
    # work it has to carry divided by its capacity, rounded up.
    lb_makespan = max(head[j] + tail[j] for j in range(n_jobs))
    for k in range(len(cap)):
        work = sum(need[j][k] * dur[j] for j in range(n_jobs))
        lb_makespan = max(lb_makespan, -(-work // cap[k]))

    # Number of time slots for the heuristic schedule: the total duration of all jobs, plus one.
    n_periods = sum(dur) + 1
    # Upper bound on the makespan: the heuristic schedule, at most the total duration of all
    # jobs and at least the lower bound.
    ub_makespan = min(sum(dur), _heuristic_makespan(dur, need, cap, preds, succs, succ, tail, n_periods))
    ub_makespan = max(ub_makespan, lb_makespan)

    # Each job starts within its window, from head[j] to latest[j]. latest[j] is the latest start
    # for which the chain of durations after job j still ends by the upper bound.
    latest = [ub_makespan - tail[j] for j in range(n_jobs)]

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # makespan: the time the last job finishes
    makespan = model.add_var("makespan", lb=lb_makespan, ub=ub_makespan, var_type=mip.INTEGER)
    # start[j]: the time job j starts
    start = [model.add_var(f"start_{j}", lb=head[j], ub=latest[j], var_type=mip.INTEGER)
             for j in range(n_jobs)]
    # started[j][t] is 1 when job j has started by time t, and 0 when not. Only the times in
    # the window have a variable.
    started = {}
    for j in range(n_jobs):
        started[j] = {t: model.add_var(f"started_{j}_{t}", var_type=mip.BINARY)
                      for t in range(head[j], latest[j])}

    # started_by(j, t): 0 before the window of job j, 1 from its latest start on, and
    # started[j][t] in between.
    def started_by(j, t):
        if t < head[j]:
            return 0
        if t >= latest[j]:
            return 1
        return started[j][t]

    # load(pairs, t): the units in use at time t by the jobs in pairs, where each pair is
    # (job, units). A job runs at time t when it has started by t and has not finished by t.
    # Returns the terms as (coefficient, variable) pairs and the constant part.
    def load(pairs, t):
        terms = []     # (coefficient, variable) pairs
        constant = 0   # the part that is fixed by the window
        for j, units in pairs:
            if units == 0 or dur[j] == 0:
                continue
            for sign, time in ((1, t), (-1, t - dur[j])):
                flag = started_by(j, time)
                if isinstance(flag, int):
                    constant += sign * units * flag
                else:
                    terms.append((sign * units, flag))
        return terms, constant

    # must_follow[i][j] is True when job j has to wait for job i through a chain of precedences.
    must_follow = [[False] * n_jobs for _ in range(n_jobs)]
    for a, b in succ:
        must_follow[a][b] = True
    for via in range(n_jobs):
        for i in range(n_jobs):
            if must_follow[i][via]:
                for j in range(n_jobs):
                    if must_follow[via][j]:
                        must_follow[i][j] = True

    # conflicts[i]: the jobs that cannot run at the same time as job i, because one of them has
    # to wait for the other or because together they need more of some resource than its capacity.
    # Jobs of zero duration never conflict.
    conflicts = [set() for _ in range(n_jobs)]
    for i in range(n_jobs):
        for j in range(n_jobs):
            if i == j or dur[i] == 0 or dur[j] == 0:
                continue
            if must_follow[i][j] or must_follow[j][i] or any(need[i][k] + need[j][k] > cap[k]
                                                              for k in range(len(cap))):
                conflicts[i].add(j)

    # cliques: the maximal groups of jobs that all conflict with each other
    cliques = []

    def bron_kerbosch(clique, candidates, excluded):
        if not candidates and not excluded:
            if len(clique) >= 2:
                cliques.append(sorted(clique))
            return
        for v in sorted(candidates):
            bron_kerbosch(clique | {v}, candidates & conflicts[v], excluded & conflicts[v])
            candidates = candidates - {v}
            excluded = excluded | {v}

    bron_kerbosch(set(), {i for i in range(n_jobs) if conflicts[i]}, set())

    # Each job starts only after its predecessors have finished. At each time t in the window
    # of job b, if b has started by t, then a has started by t minus the duration of a.
    for a, b in succ:
        dur_a = dur[a]
        for t in range(head[b], latest[b]):
            before = started_by(a, t - dur_a)
            if isinstance(before, int):
                if before == 0:
                    model.add_constr(started[b][t] <= 0)
            else:
                model.add_constr(started[b][t] <= before)
        # a has started by the latest start of b minus its duration, so b can still start in time.
        last = started_by(a, latest[b] - dur_a)
        if not isinstance(last, int):
            model.add_constr(last >= 1)

    # Once started, a job stays started. The start time is the latest start minus the number
    # of 1 flags in the window.
    for j in range(n_jobs):
        for t in range(head[j], latest[j] - 1):
            model.add_constr(started[j][t] <= started[j][t + 1])
        model.add_constr(start[j] + mip.xsum(started[j].values()) == latest[j])

    # The makespan is at least the finish time of every job.
    for j in range(n_jobs):
        model.add_constr(makespan >= start[j] + dur[j])

    # Jobs that conflict with each other cannot run together: in each maximal group, at most
    # one job runs at a time.
    for clique in cliques:
        for t in range(ub_makespan):
            terms, constant = load([(j, 1) for j in clique], t)
            # Rows that no choice can violate are left out.
            if not terms or sum(c for c, _ in terms if c > 0) + constant <= 1:
                continue
            model.add_constr(mip.xsum(c * v for c, v in terms) <= 1 - constant)

    # Each resource: at each time, the units used by the jobs running then stay within its
    # capacity. A job started at time s runs at the times s to s + duration - 1.
    for k in range(len(cap)):
        # A resource whose total need fits its capacity cannot be over it.
        if sum(need[j][k] for j in range(n_jobs)) <= cap[k]:
            continue
        for t in range(ub_makespan):
            terms, constant = load([(j, need[j][k]) for j in range(n_jobs)], t)
            # Rows that no choice can violate are left out.
            if not terms or sum(c for c, _ in terms if c > 0) + constant <= cap[k]:
                continue
            model.add_constr(mip.xsum(c * v for c, v in terms) <= cap[k] - constant)

    # Minimise the makespan.
    model.objective = makespan
    return model, {"start_time": start}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
