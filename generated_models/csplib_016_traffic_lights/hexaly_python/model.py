"""Traffic lights: states for four vehicle and four pedestrian lights so that every pair of crossing roads is safe."""
import hexaly.optimizer as hx


def build(instance):
    allowed = instance["allowed_tuples"]  # safe combinations (V_i, P_i, V_i+1, P_i+1)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Vehicle lights: 0 red, 1 red-yellow, 2 green, 3 yellow; pedestrian lights: 0 red, 1 green
    v = [model.int(0, 3) for _ in range(4)]
    p = [model.int(0, 1) for _ in range(4)]

    # For each pair of neighbouring roads (the fourth wrapping round to the first), the
    # combination of their four lights is one of the allowed tuples
    for i in range(4):
        j = (i + 1) % 4
        model.constraint(model.or_(*[model.and_(v[i] == a, p[i] == b, v[j] == c, p[j] == d)
                                     for a, b, c, d in allowed]))

    # The lights in the order V1, V2, V3, V4, P1, P2, P3, P4
    return optimizer, {"lights": v + p}
