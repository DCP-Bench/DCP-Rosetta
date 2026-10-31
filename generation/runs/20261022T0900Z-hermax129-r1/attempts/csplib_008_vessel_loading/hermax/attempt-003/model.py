from hermax.model import Model


def build(instance):
    deck_w = instance["deck_width"]
    deck_l = instance["deck_length"]
    width = instance["width"]
    length = instance["length"]
    classes = instance["classes"]
    separation = instance["separation"]
    n = len(width)

    m = Model()
    left = m.int_vector("left", n, 0, deck_w)
    right = m.int_vector("right", n, 0, deck_w)
    bottom = m.int_vector("bottom", n, 0, deck_l)
    top = m.int_vector("top", n, 0, deck_l)
    rotated = m.bool_vector("rotated", n)

    # Each container occupies its width and length along the deck axes,
    # swapped when it is rotated by 90 degrees.
    for i in range(n):
        m &= (right[i] - left[i] == width[i]).only_if(~rotated[i])
        m &= (top[i] - bottom[i] == length[i]).only_if(~rotated[i])
        m &= (right[i] - left[i] == length[i]).only_if(rotated[i])
        m &= (top[i] - bottom[i] == width[i]).only_if(rotated[i])

    # Containers must not overlap. For each pair, one of the four sides must
    # separate them by the required distance for their classes (0 when the
    # classes have no separation requirement between them).
    for i in range(n):
        for j in range(i + 1, n):
            s = separation[classes[i] - 1][classes[j] - 1]
            sides = [
                left[j] - right[i] >= s,   # j lies to the right of i
                left[i] - right[j] >= s,   # i lies to the right of j
                bottom[j] - top[i] >= s,   # j lies above i
                bottom[i] - top[j] >= s,   # i lies above j
            ]
            lits = []
            for side in sides:
                r = m.bool()
                m &= side.iff(r)
                lits.append(r)
            m &= (lits[0] | lits[1] | lits[2] | lits[3])

    outputs = {"left": left, "right": right, "top": top, "bottom": bottom}
    return m, outputs
