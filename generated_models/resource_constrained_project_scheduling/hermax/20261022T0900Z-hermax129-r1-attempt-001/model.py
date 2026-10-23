from hermax.model import Model


def build(instance):
    durations = instance["durations_data"]
    needs = instance["resource_needs_data"]
    capacities = instance["resource_capacities_data"]
    successors = instance["successors_link_data"]

    n = len(durations)
    # Sum of all durations is a valid horizon: serial scheduling fits in it.
    horizon = sum(durations)

    m = Model()

    # Start time of each job, from 0 to the horizon.
    start = m.int_vector("start_time", n, 0, horizon)

    # Precedence: a job starts only after each of its predecessors has finished.
    for pred, succ in successors:
        m &= (start[succ] >= start[pred] + durations[pred])

    # Resource capacity: at every time, the jobs running use at most the capacity
    # of each renewable resource.
    for r, cap in enumerate(capacities):
        demands = [needs[j][r] for j in range(n)]
        m.cumulative(start, durations, demands, cap)

    # The sink job (last index, duration 0) finishes after every job, so its start
    # time is the makespan.
    sink = n - 1
    for j in range(n):
        m &= (start[sink] >= start[j] + durations[j])

    # Minimise the makespan.
    m.obj += start[sink]

    return m, {"start_time": start}
