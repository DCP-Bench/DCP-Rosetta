# flowshop_scheduling: a PyCSP3 model from DCP Rosetta.
# Download the `flowshop_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python flowshop_scheduling.py flowshop_scheduling.json

from pycsp3 import *


def create_model(instance):
    """Jobs are processed on machines 1 to M in series, every job going through the machines
    in the same order: a machine works on one job at a time, and a job moves to the next
    machine when it has finished on the one before. Find the sequence of jobs that minimises
    the makespan, the time when all jobs have been processed."""
    process_time = instance["process_time"]  # process_time[j][m] is the time job j takes on machine m
    # The fields jobs and machines only number the jobs and machines, and schedules is a given sequence; the model chooses the sequence itself and takes both counts from process_time.
    n_jobs = len(process_time)
    n_machines = len(process_time[0])
    # The job positions 0 to n_jobs - 1 in the sequence, and the machines 0 to n_machines - 1.
    positions = range(n_jobs)
    machines = range(n_machines)
    # A processing time is at most the longest one in process_time (the bound of the duration variables).
    longest = max(max(row) for row in process_time)
    # The jobs run one after another on the machines, so the sum of all processing times bounds the makespan.
    horizon = sum(sum(row) for row in process_time)

    # sequence[k] is the job at position k of the sequence.
    sequence = VarArray(size=n_jobs, dom=range(n_jobs))
    # duration[k][m] is the processing time on machine m of the job at position k.
    duration = VarArray(size=[n_jobs, n_machines], dom=range(longest + 1))
    # start[k][m] is the time the job at position k starts on machine m.
    start = VarArray(size=[n_jobs, n_machines], dom=range(horizon + 1))
    # makespan is the time when all jobs have been processed.
    makespan = Var(dom=range(horizon + 1))

    satisfy(
        # Every job occupies exactly one position in the sequence.
        AllDifferent(sequence),
        # The job at each position takes its own processing time on each machine (a Table, since a plain list cannot be indexed by the variable sequence[k]).
        [Table(scope=[sequence[k], duration[k][m]],
               supports=[(j, process_time[j][m]) for j in range(n_jobs)])
         for k in positions for m in machines],
        # A job starts on a machine only after it has finished on the machine before.
        [start[k][m1] + duration[k][m1] <= start[k][m2]
         for k in positions for m1, m2 in zip(machines, machines[1:])],
        # A machine works on one job at a time: the job at a position starts on a machine only after the job before it in the sequence has left that machine.
        [start[k1][m] + duration[k1][m] <= start[k2][m]
         for k1, k2 in zip(positions, positions[1:]) for m in machines],
        # The makespan is when the last job leaves the last machine; the jobs stay in sequence on each machine, so that is the latest finish.
        makespan == start[n_jobs - 1][n_machines - 1] + duration[n_jobs - 1][n_machines - 1],
    )

    # The makespan is as small as possible.
    minimize(makespan)

    return {"makespan": makespan}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
