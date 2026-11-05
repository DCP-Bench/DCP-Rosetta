"""Resource-constrained project scheduling: start the jobs respecting precedences and resource capacities,
minimising the makespan."""
import hexaly.optimizer as hx


def build(instance):
    # durations_data[j] = duration of job j in time units;
    # resource_needs_data[j][r] = units of resource r that job j uses at every time unit while it runs
    duration, needs = instance["durations_data"], instance["resource_needs_data"]
    # resource_capacities_data[r] = units of resource r available at any time;
    # successors_link_data = (predecessor, successor) pairs of job indices: the predecessor
    # must finish before the successor starts
    capacity, links = instance["resource_capacities_data"], instance["successors_link_data"]
    n, resources = len(duration), len(capacity)  # number of jobs, number of resource types
    # Upper bound on the makespan (derived): running the jobs one after another takes sum(duration),
    # which respects the precedences, so an optimum finishes by then
    horizon = sum(duration)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # start_time[j] = the time unit at which job j starts (0 is the project start); it cannot start so late that
    # it ends after the horizon
    start_time = [model.int(0, horizon - duration[j]) for j in range(n)]
    # end[j] = the time at which job j finishes (start plus duration)
    end = [start_time[j] + duration[j] for j in range(n)]

    # Precedence: a job starts only after each of its predecessors has finished
    for pred, succ in links:
        model.constraint(start_time[succ] >= end[pred])
    # Resource capacities: at every time unit the running jobs use at most each resource's capacity.
    # (Time is discrete, so each time unit t from 0 to horizon - 1 is checked; jobs of duration 0 never run.)
    for t in range(horizon):
        # running[k] = 1 if job users[k] is in progress at time t (started by t and not yet finished)
        running = [model.and_(start_time[j] <= t, t < end[j]) for j in range(n) if duration[j] > 0]
        users = [j for j in range(n) if duration[j] > 0]
        for r in range(resources):
            model.constraint(model.sum(needs[j][r] * on for j, on in zip(users, running) if needs[j][r]) <= capacity[r])

    # Minimise the makespan, when the last job finishes
    model.minimize(model.max(end))
    return optimizer, {"start_time": start_time}
