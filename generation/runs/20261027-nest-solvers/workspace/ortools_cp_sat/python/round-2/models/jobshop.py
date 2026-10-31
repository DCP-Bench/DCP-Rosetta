import json
import sys

from ortools.sat.python import cp_model


def main():
    with open(sys.argv[1]) as f:
        data = json.load(f)
    jobs = data["jobs"]
    horizon = sum(d for job in jobs for _, d in job)

    model = cp_model.CpModel()
    starts = []
    ends_last = []
    machine_intervals = {}
    for j, job in enumerate(jobs):
        row = []
        prev_end = None
        for k, (machine, duration) in enumerate(job):
            start = model.new_int_var(0, horizon, f"start_{j}_{k}")
            end = model.new_int_var(0, horizon, f"end_{j}_{k}")
            interval = model.new_interval_var(start, duration, end, f"task_{j}_{k}")
            machine_intervals.setdefault(machine, []).append(interval)
            if prev_end is not None:
                model.add(start >= prev_end)
            prev_end = end
            row.append(start)
        starts.append(row)
        ends_last.append(prev_end)

    # One no-overlap per machine, not one over all tasks.
    for intervals in machine_intervals.values():
        model.add_no_overlap(intervals)

    makespan = model.new_int_var(0, horizon, "makespan")
    for end in ends_last:
        model.add(makespan >= end)
    model.minimize(makespan)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    status = solver.solve(model)
    if status != cp_model.OPTIMAL:
        print(solver.status_name(status), file=sys.stderr)
        sys.exit(1)
    print(json.dumps({"start": [[solver.value(s) for s in row] for row in starts]}))


if __name__ == "__main__":
    main()
