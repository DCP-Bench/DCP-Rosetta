# jobshop: a CPLEX (Python) model from DCP Rosetta.
# Download the `jobshop.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobshop.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python jobshop.py jobshop.json

from docplex.mp.model import Model


def create_model(instance):
    """Job shop scheduling: every job is a sequence of tasks, each needing one machine for a given
    duration. A job's tasks run in order, a machine runs one task at a time, and the makespan (the
    time the last task ends) is to be minimised."""
    jobs_data = instance["jobs_data"]  # jobs_data[job][task] = [machine, duration]
    # Horizon: running all tasks one after another is always a valid schedule and takes the sum
    # of all durations, so no optimal schedule needs a task to end later; it keeps the times finite.
    horizon = sum(duration for job in jobs_data for _, duration in job)

    model = Model("jobshop")

    # start[j, t] is the start time of task t of job j; it ends after its duration.
    start = {(j, t): model.integer_var(0, horizon, name=f"start_{j}_{t}")
             for j, job in enumerate(jobs_data) for t in range(len(job))}
    # end[j, t] is the time at which task t of job j ends.
    end = {(j, t): start[j, t] + jobs_data[j][t][1] for (j, t) in start}

    # Every task ends within the horizon.
    model.add_constraints(end[key] <= horizon for key in start)

    # No task can start before the previous task of its job ends.
    model.add_constraints(start[j, t] >= end[j, t - 1]
                          for j, job in enumerate(jobs_data) for t in range(1, len(job)))

    # Two tasks on the same machine do not overlap: one of them starts after the other ends.
    # For each pair, first is 1 when the first task of the pair goes before the second.
    machines = sorted({machine for job in jobs_data for machine, _ in job})
    for machine in machines:
        tasks = [(j, t) for j, job in enumerate(jobs_data) for t, (m, _) in enumerate(job) if m == machine]
        for a in range(len(tasks)):
            for b in range(a + 1, len(tasks)):
                one, two = tasks[a], tasks[b]
                first = model.binary_var(name=f"first_{one[0]}_{one[1]}_{two[0]}_{two[1]}")
                model.add_indicator(first, start[two] >= end[one], active_value=1)
                model.add_indicator(first, start[one] >= end[two], active_value=0)

    # The makespan is the latest end time: at least the end of every job's last task (the
    # last task of a job ends after all its others), and minimisation makes it equal.
    makespan = model.integer_var(0, horizon, name="makespan")
    model.add_constraints(makespan >= end[j, len(job) - 1] for j, job in enumerate(jobs_data) if job)

    # Objective: minimise the makespan.
    model.minimize(makespan)

    return model, {"makespan": makespan}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
