# flowshop_scheduling: a CPMpy model from DCP Rosetta.
# Download the `flowshop_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flowshop_scheduling.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python flowshop_scheduling.py flowshop_scheduling.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """A set of jobs is processed on a series of machines, every job visiting the machines
    in the same order from machine 1 to machine M, and all machines handling the jobs in one
    common sequence. Find the sequence that minimises the makespan, the time when all jobs
    have been processed."""
    process_time = np.array(instance["process_time"])  # process_time[j][m]: time of job j on machine m
    n_jobs, n_machines = process_time.shape

    # Everything fits within the sum of all processing times (a schedule with no overlap).
    horizon = int(process_time.sum())

    # sequence[k] is the job processed in position k.
    sequence = cp.intvar(0, n_jobs - 1, shape=n_jobs, name="sequence")
    # start_times[k, m] and end_times[k, m]: start and end time of the k-th job of the
    # sequence on machine m.
    start_times = cp.intvar(0, horizon, shape=(n_jobs, n_machines), name="start_times")
    end_times = cp.intvar(0, horizon, shape=(n_jobs, n_machines), name="end_times")
    # makespan is the time when the last job leaves the last machine.
    makespan = cp.intvar(0, horizon, name="makespan")

    model = cp.Model()

    # Every job appears exactly once in the sequence.
    model.add(cp.AllDifferent(sequence))

    # A job occupies each machine for its processing time on that machine.
    for m in range(n_machines):
        model.add(end_times[:, m] == start_times[:, m] + cp.cpm_array(process_time[:, m])[sequence])

    # A job cannot start on machine m before it has finished on machine m-1.
    model.add(start_times[:, 1:] >= end_times[:, :-1])

    # A machine handles one job at a time: the k-th job of the sequence cannot start
    # before the (k-1)-th job has left that machine.
    model.add(start_times[1:, :] >= end_times[:-1, :])

    # The makespan is the latest completion time.
    model.add(makespan == cp.max(end_times))
    model.minimize(makespan)

    return model, {"makespan": makespan}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
