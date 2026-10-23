from hermax.model import Model


def build(instance):
    # The safe (V_i, P_i, V_{i+1}, P_{i+1}) combinations come from the instance.
    allowed = [tuple(t) for t in instance["allowed_tuples"]]
    n = 4  # number of junction roads, fixed by the problem (8 lights)

    # lights = [V1..Vn, P1..Pn]. Vehicle states 0..3, pedestrian states 0..1.
    m = Model()
    lights = m.int_vector("lights", 2 * n, 0, 3)
    for k in range(n):
        m &= (lights[n + k] <= 1)  # pedestrian states are red (0) or green (1)

    # Each road i pairs light i with light i+1 (wrapping around), vehicles and pedestrians.
    for i in range(n):
        j = (i + 1) % n
        m &= m.table(
            [lights[i], lights[n + i], lights[j], lights[n + j]],
            allowed=allowed,
        )

    return m, {"lights": lights}
