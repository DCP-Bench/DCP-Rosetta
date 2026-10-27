import json
import sys

from ortools.sat.python import cp_model

with open(sys.argv[1]) as f:
    data = json.load(f)

jobs = data["jobs"]
horizon = sum(d for job in jobs for _, d in job)

model = cp_model.CpModel()
starts = []
per_machine = {}
ends = []
for j, job in enumerate(jobs):
    job_starts = []
    job_ends = []
    for k, (machine, duration) in enumerate(job):
        s = model.new_int_var(0, horizon, f"s_{j}_{k}")
        e = model.new_int_var(0, horizon, f"e_{j}_{k}")
        iv = model.new_interval_var(s, duration, e, f"i_{j}_{k}")
        per_machine.setdefault(machine, []).append(iv)
        job_starts.append(s)
        job_ends.append(e)
        if k > 0:
            model.add(s >= job_ends[k - 1])
    starts.append(job_starts)
    ends.extend(job_ends[-1:])

for machine, intervals in per_machine.items():
    model.add_no_overlap(intervals)

makespan = model.new_int_var(0, horizon, "makespan")
model.add_max_equality(makespan, ends)
model.minimize(makespan)

solver = cp_model.CpSolver()
status = solver.solve(model)
if status != cp_model.OPTIMAL:
    raise SystemExit(solver.status_name(status))

print(json.dumps({"start": [[solver.value(s) for s in row] for row in starts]}))
