from hermax.model import Model


def build(instance):
    W = instance["deck_width"]
    L = instance["deck_length"]
    n = instance["n_containers"]
    widths = instance["width"]
    lengths = instance["length"]
    classes = instance["classes"]
    sep = instance["separation"]

    m = Model()

    # Positions use edge coordinates: a container spans [left, right) along
    # the width and [top, bottom) along the length, so right = left + extent.
    left = m.int_vector("left", n, 0, W)
    right = m.int_vector("right", n, 0, W)
    top = m.int_vector("top", n, 0, L)
    bottom = m.int_vector("bottom", n, 0, L)

    # Containers may be rotated 90 degrees: rot[i] true swaps width and length.
    rot = m.bool_vector("rot", n)
    ew = [m.int(f"ew_{i}", min(widths[i], lengths[i]), max(widths[i], lengths[i]))
          for i in range(n)]
    eh = [m.int(f"eh_{i}", min(widths[i], lengths[i]), max(widths[i], lengths[i]))
          for i in range(n)]
    for i in range(n):
        # Extent along the deck width and length follows the orientation.
        m &= (~rot[i]) | (ew[i] == lengths[i])
        m &= rot[i] | (ew[i] == widths[i])
        m &= (~rot[i]) | (eh[i] == widths[i])
        m &= rot[i] | (eh[i] == lengths[i])
        # The container stays on the deck.
        m &= (right[i] == left[i] + ew[i])
        m &= (bottom[i] == top[i] + eh[i])

    # Non-overlap and separation: each pair is apart by at least the required
    # distance s along the deck width or along the deck length. s is the
    # separation between the two classes; s = 0 gives plain non-overlap.
    for i in range(n):
        for j in range(i + 1, n):
            s = sep[classes[i] - 1][classes[j] - 1]
            s = max(s, 0)
            j_right_of_i = m.bool()
            i_right_of_j = m.bool()
            j_below_i = m.bool()
            i_below_j = m.bool()
            m &= (left[j] >= right[i] + s).iff(j_right_of_i)
            m &= (left[i] >= right[j] + s).iff(i_right_of_j)
            m &= (top[j] >= bottom[i] + s).iff(j_below_i)
            m &= (top[i] >= bottom[j] + s).iff(i_below_j)
            m &= (j_right_of_i | i_right_of_j | j_below_i | i_below_j)

    return m, {"left": left, "right": right, "top": top, "bottom": bottom}
