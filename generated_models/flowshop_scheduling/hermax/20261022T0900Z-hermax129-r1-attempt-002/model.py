from hermax.model import Model


def build(instance):
    t = instance["process_time"]          # t[job][machine]
    n = len(instance["jobs"])
    M = len(instance["machines"])
    horizon = sum(sum(row) for row in t)  # every job on every machine, back to back
    width = horizon.bit_length()

    m = Model()

    # x[j][p] is true when job j is in position p of the sequence.
    x = m.bool_matrix("x", n, n)
    for j in range(n):
        m &= x.row(j).exactly_one()
    for p in range(n):
        m &= x.col(p).exactly_one()

    # Processing time of the job in position p on machine k.
    def proc(p, k):
        return sum(t[j][k] * x[j][p] for j in range(n))

    # Completion time of the job in position p on machine k, as a weighted sum
    # of binary digits. Integer variables with a wide domain are costly to
    # compare with each other, so the times live only as digit sums.
    C = [[None] * M for _ in range(n)]
    for p in range(n):
        for k in range(M):
            bits = m.bool_vector(f"cb_{p}_{k}", width)
            C[p][k] = sum(2 ** b * bits[b] for b in range(width))
            m &= (C[p][k] <= horizon)

    # A job starts on a machine after it leaves the previous machine and after
    # the previous job leaves this machine. Only lower bounds are posted: the
    # objective pushes every completion time down to its tightest value.
    for p in range(n):
        for k in range(M):
            if p == 0 and k == 0:
                m &= (C[p][k] - proc(p, k) >= 0)
            if p > 0:
                m &= (C[p][k] - C[p - 1][k] - proc(p, k) >= 0)
            if k > 0:
                m &= (C[p][k] - C[p][k - 1] - proc(p, k) >= 0)

    # Minimise the makespan: completion of the last job on the last machine.
    m.obj += C[n - 1][M - 1]

    # The declared output is an integer tied to that completion time.
    makespan = m.int("makespan", 0, horizon)
    m &= (makespan == C[n - 1][M - 1])

    return m, {"makespan": makespan}
