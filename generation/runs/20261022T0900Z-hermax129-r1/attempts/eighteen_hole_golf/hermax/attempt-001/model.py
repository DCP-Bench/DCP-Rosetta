from hermax.model import Model


def build(instance):
    m = Model()

    # Create 18 holes, each with length 3, 4, or 5
    holes = m.int_vector("holes", 18, 3, 5)

    # The total length of the course must be 72
    m &= (sum(holes) == 72)

    return m, {"holes": holes}
