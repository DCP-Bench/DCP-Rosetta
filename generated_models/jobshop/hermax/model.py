# jobshop: a hermax (Python) model from DCP Rosetta.
# Download the `jobshop.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
# Then run it on the first instance (after `pip install hermax`):
#   python jobshop.py jobshop.json

from hermax.model import Model


def create_model(instance):
    """Schedule the tasks of every job on their machines so that the last task finishes as early as possible.

    Each job is a chain of tasks that must run one after another. Each task runs on one machine
    for its duration, a machine works on one task at a time, and a task, once started, runs to
    completion. The objective is the makespan: the time at which all jobs are complete.
    """
    # jobs_data[j][t] = [machine, duration]: task t of job j runs on that machine for that long
    jobs_data = instance["jobs_data"]

    # Horizon: running every task one after another is a feasible schedule, so no task
    # needs to start after the total of all durations. It bounds every start time and the makespan.
    horizon = sum(duration for job in jobs_data for _, duration in job)

    m = Model()

    # start[j][t] is when task t of job j starts. Its window follows from its own job: it cannot
    # start before the earlier tasks of the job have run, and the task and the later tasks of the
    # job must still fit before the horizon.
    start = [[m.int(f"start_{j}_{t}", sum(d for _, d in job[:t]), horizon - sum(d for _, d in job[t:]))
              for t in range(len(job))]
             for j, job in enumerate(jobs_data)]

    # makespan is the time at which the last task finishes (the declared output); it is at
    # least the total duration of the longest job
    makespan = m.int("makespan", max(sum(d for _, d in job) for job in jobs_data), horizon)

    # A task starts only after the previous task of its job has finished.
    for j, job in enumerate(jobs_data):
        for t in range(1, len(job)):
            m &= (start[j][t - 1] + job[t - 1][1] <= start[j][t])
        # The makespan is not before the end of the last task of every job.
        last = len(job) - 1
        m &= (start[j][last] + job[last][1] <= makespan)

    # A machine works on one task at a time: of any two tasks on the same machine, one
    # finishes before the other starts. first is true when the earlier-listed task of the pair goes first.
    # (m.cumulative(..., [1] * k, 1) per machine says the same, but took 84 s against
    # 10 s with these pairwise orderings on a 10-job, 5-machine instance.)
    # every task as (job, index in job)
    tasks = [(j, t) for j, job in enumerate(jobs_data) for t in range(len(job))]
    for x, (j1, t1) in enumerate(tasks):
        for (j2, t2) in tasks[x + 1:]:
            machine1, duration1 = jobs_data[j1][t1]
            machine2, duration2 = jobs_data[j2][t2]
            if machine1 != machine2 or j1 == j2:
                continue  # tasks of one job are already ordered by the precedences
            first = m.bool()
            m &= (start[j1][t1] + duration1 <= start[j2][t2]).only_if(first)
            m &= (start[j2][t2] + duration2 <= start[j1][t1]).only_if(~first)

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
