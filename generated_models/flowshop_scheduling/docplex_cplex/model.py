# flowshop_scheduling: a CPLEX (Python) model from DCP Rosetta.
# Download the `flowshop_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python flowshop_scheduling.py flowshop_scheduling.json

from docplex.mp.model import Model


def create_model(instance):
    """Permutation flow shop: every job visits the machines in the same order, and all machines
    process the jobs in one common sequence. Find the sequence and start times that minimise the
    makespan, the time the last job finishes on the last machine."""
    process_time = instance["process_time"]  # process_time[j][m]: time of job j on machine m
    n_jobs = len(instance["jobs"])          # the jobs to sequence
    n_machines = len(instance["machines"])  # the machines every job passes through, in order
    jobs = range(n_jobs)
    machines = range(n_machines)
    slots = range(n_jobs)
    # An upper bound on every time, chosen to keep the variables finite: running the jobs one
    # after another takes the sum of all processing times, so no optimal makespan is larger.
    max_duration = sum(sum(row) for row in process_time)

    model = Model("flowshop_scheduling")

    # in_slot[k, j] is 1 when job j is the k-th job of the sequence.
    in_slot = {(k, j): model.binary_var(name=f"in_slot_{k}_{j}") for k in slots for j in jobs}
    # Every slot of the sequence holds one job and every job sits in one slot.
    model.add_constraints(model.sum(in_slot[k, j] for j in jobs) == 1 for k in slots)
    model.add_constraints(model.sum(in_slot[k, j] for k in slots) == 1 for j in jobs)

    # start[k, m] is the start time of the k-th job of the sequence on machine m; it ends after
    # that job's processing time on machine m.
    start = {(k, m): model.continuous_var(0, max_duration, name=f"start_{k}_{m}") for k in slots for m in machines}
    duration = {(k, m): model.sum(process_time[j][m] * in_slot[k, j] for j in jobs) for k in slots for m in machines}
    end = {(k, m): start[k, m] + duration[k, m] for k in slots for m in machines}

    for k in slots:
        for m in machines:
            # A job cannot start on machine m before it has completed on machine m-1.
            if m > 0:
                model.add_constraint(start[k, m] >= end[k, m - 1])
            # The k-th job cannot start on machine m before the (k-1)-th has completed on it.
            if k > 0:
                model.add_constraint(start[k, m] >= end[k - 1, m])

    # The makespan is the latest end time. With the two orderings above, the last job on the
    # last machine ends last, so the makespan is at least that end time; minimisation makes it
    # equal.
    makespan = model.integer_var(0, max_duration, name="makespan")
    model.add_constraint(makespan >= end[n_jobs - 1, n_machines - 1])

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
