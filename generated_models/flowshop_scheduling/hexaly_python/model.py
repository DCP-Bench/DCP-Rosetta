"""Permutation flow shop: one job order through every machine in series, minimising the makespan."""
import hexaly.optimizer as hx


def build(instance):
    p = instance["process_time"]  # p[j][m]: time of job j on machine m
    n, machines = len(p), len(p[0])
    horizon = sum(sum(row) for row in p)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # at[j][k] = 1 if job j is the k-th of the sequence: every job in one place, one job per place
    at = [[model.bool() for _ in range(n)] for _ in range(n)]
    for j in range(n):
        model.constraint(model.sum(at[j]) == 1)
    for k in range(n):
        model.constraint(model.sum(at[j][k] for j in range(n)) == 1)
    # The processing time of the k-th job of the sequence on machine m
    time = [[model.sum(p[j][m] * at[j][k] for j in range(n)) for m in range(machines)] for k in range(n)]

    # done[k][m] is when the k-th job leaves machine m. A job starts on a machine once it has left
    # the previous machine and the machine has finished the previous job; at the minimum these
    # linear lower bounds are met with equality.
    done = [[model.int(0, horizon) for _ in range(machines)] for _ in range(n)]
    for k in range(n):
        for m in range(machines):
            model.constraint(done[k][m] >= time[k][m] + (done[k][m - 1] if m else 0))
            if k:
                model.constraint(done[k][m] >= time[k][m] + done[k - 1][m])

    # Minimise the makespan, when the last job leaves the last machine
    makespan = done[n - 1][machines - 1]
    model.minimize(makespan)
    return optimizer, {"makespan": makespan}
