# flowshop_scheduling: a hermax (Python) model from DCP Rosetta.
# Download the `flowshop_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
# Then run it on the first instance (after `pip install hermax`):
#   python flowshop_scheduling.py flowshop_scheduling.json

from hermax.model import Model


def create_model(instance):
    """Permutation flow shop: every job visits machines 1..M in that order, all jobs use the
    machines in the same sequence, and a machine works on one job at a time. Choose the
    sequence of jobs that minimises the makespan, the time the last job leaves the last machine."""
    process_time = instance["process_time"]  # process_time[j][k]: time job j needs on machine k
    n_jobs = len(process_time)  # number of jobs
    n_machines = len(process_time[0])  # number of machines

    # Time windows for the start times, derived from the data. head[j][k] is the time job j
    # needs on the machines before k (it cannot start on machine k earlier); tail[j][k] is the
    # time from its start on machine k until it has left the last machine.
    head = [[sum(process_time[j][:k]) for k in range(n_machines)] for j in range(n_jobs)]
    tail = [[sum(process_time[j][k:]) for k in range(n_machines)] for j in range(n_jobs)]
    # Lower bound on the makespan: the longest single job, and for each machine the time before
    # the first job reaches it, plus all the work on it, plus the least work after it.
    lower = max(tail[j][0] for j in range(n_jobs))
    for k in range(n_machines):
        before_k = min(head[j][k] for j in range(n_jobs))
        work_k = sum(process_time[j][k] for j in range(n_jobs))
        after_k = min(tail[j][k] - process_time[j][k] for j in range(n_jobs))
        lower = max(lower, before_k + work_k + after_k)
    # Upper bound: the makespan of one feasible sequence, the jobs by decreasing total time.
    # The optimum cannot be longer, so no start time needs to go past it.
    sequence = sorted(range(n_jobs), key=lambda j: -sum(process_time[j]))
    done = [0] * n_machines  # when each machine finishes the jobs handled so far
    for j in sequence:
        ready = 0  # when job j leaves the previous machine
        for k in range(n_machines):
            ready = max(ready, done[k]) + process_time[j][k]
            done[k] = ready
    # The +1 only keeps the domain of makespan from being a single value (lower == horizon).
    # hermax's m.int accepts lo == hi (tested), so this is a harmless safeguard, not a requirement.
    horizon = max(done[-1], lower + 1)

    m = Model()

    # horizon - tail[j][k] >= head[j][k] always holds; the max(..., head + 1) padding likewise only
    # avoids a single-value domain (lo == hi is accepted by m.int, so it is not required).
    # start[j][k] is the time job j starts on machine k, inside its own time window
    start = [[m.int(f"start_{j}_{k}", head[j][k], max(horizon - tail[j][k], head[j][k] + 1))
              for k in range(n_machines)]
             for j in range(n_jobs)]
    # makespan is the time the last job leaves the last machine (the declared output)
    makespan = m.int("makespan", lower, horizon)

    # before[(j, i)] for j < i is true when job j comes before job i in the sequence. The same
    # order holds on every machine, which is what makes the schedule a permutation flow shop.
    before = {(j, i): m.bool(f"before_{j}_{i}") for j in range(n_jobs) for i in range(j + 1, n_jobs)}

    # Each job goes to the next machine only after it has finished on the previous one.
    for j in range(n_jobs):
        for k in range(1, n_machines):
            m &= (start[j][k - 1] + process_time[j][k - 1] <= start[j][k])

    # The makespan is not before the end of any job on the last machine.
    last = n_machines - 1
    for j in range(n_jobs):
        m &= (start[j][last] + process_time[j][last] <= makespan)

    # On each machine, two jobs do not overlap: the earlier one in the sequence finishes before
    # the later one starts. Each order is one half-reified constraint.
    for k in range(n_machines):
        for (j, i), j_first in before.items():
            m &= (start[j][k] + process_time[j][k] <= start[i][k]).only_if(j_first)
            m &= (start[i][k] + process_time[i][k] <= start[j][k]).only_if(~j_first)

    # The sequence is a total order, so "before" is transitive: if j is before i and i is before h,
    # then j is before h, and no three jobs form a cycle. The start times already rule out cycles;
    # these clauses only help the solver see it without searching times.
    for j in range(n_jobs):
        for i in range(j + 1, n_jobs):
            for h in range(i + 1, n_jobs):
                m &= (~before[(j, i)] | ~before[(i, h)] | before[(j, h)])
                m &= (before[(j, i)] | before[(i, h)] | ~before[(j, h)])

    # Minimise the makespan.
    m.obj += makespan

    return m, {"makespan": makespan}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
