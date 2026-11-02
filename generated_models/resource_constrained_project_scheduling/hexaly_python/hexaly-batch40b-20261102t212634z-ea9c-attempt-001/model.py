"""Resource-constrained project scheduling: start the jobs respecting precedences and resource capacities,
minimising the makespan."""
import hexaly.optimizer as hx


def build(instance):
    duration, needs = instance["durations_data"], instance["resource_needs_data"]
    capacity, links = instance["resource_capacities_data"], instance["successors_link_data"]
    n, resources = len(duration), len(capacity)
    horizon = sum(duration)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    start_time = [model.int(0, horizon - duration[j]) for j in range(n)]
    end = [start_time[j] + duration[j] for j in range(n)]

    # A job starts only after each of its predecessors has finished
    for pred, succ in links:
        model.constraint(start_time[succ] >= end[pred])
    # At every time unit the running jobs use at most each resource's capacity
    for t in range(horizon):
        running = [model.and_(start_time[j] <= t, t < end[j]) for j in range(n) if duration[j] > 0]
        users = [j for j in range(n) if duration[j] > 0]
        for r in range(resources):
            model.constraint(model.sum(needs[j][r] * on for j, on in zip(users, running) if needs[j][r]) <= capacity[r])

    # Minimise the makespan, when the last job finishes
    model.minimize(model.max(end))
    return optimizer, {"start_time": start_time}
