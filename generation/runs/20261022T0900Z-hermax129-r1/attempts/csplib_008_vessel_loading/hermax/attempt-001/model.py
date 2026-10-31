from hermax.model import Model


def build(instance):
    # Read instance data
    n_containers = instance["n_containers"]
    deck_length = instance["deck_length"]
    deck_width = instance["deck_width"]
    length = instance["length"]  # length[i] for container i
    width = instance["width"]    # width[i] for container i
    classes = instance["classes"]  # classes[i] for container i
    separation = instance["separation"]  # separation[class_a][class_b]

    m = Model()

    # Decision variables: left and bottom position of each container
    left = m.int_vector("left", n_containers, 0, deck_length)
    bottom = m.int_vector("bottom", n_containers, 0, deck_width)

    # Derived: right and top positions
    right = m.int_vector("right", n_containers, 0, deck_length)
    top = m.int_vector("top", n_containers, 0, deck_width)

    # Constraint group 1: compute right and top from left and bottom
    for i in range(n_containers):
        m &= (right[i] == left[i] + length[i])
        m &= (top[i] == bottom[i] + width[i])

    # Constraint group 2: containers fit on deck
    for i in range(n_containers):
        m &= (left[i] >= 0)
        m &= (right[i] <= deck_length)
        m &= (bottom[i] >= 0)
        m &= (top[i] <= deck_width)

    # Constraint group 3: no overlapping containers (pairwise)
    # Two rectangles don't overlap if one is completely to the left, right, above, or below the other
    for i in range(n_containers):
        for j in range(i + 1, n_containers):
            # Create variables for each possible non-overlap condition
            left_of = m.bool(f"left_{i}_{j}")  # i is to the left of j
            above = m.bool(f"above_{i}_{j}")   # i is above j

            # left_of is true iff right[i] <= left[j]
            m &= (left_of == (right[i] <= left[j]))
            # above is true iff top[i] <= bottom[j]
            m &= (above == (top[i] <= bottom[j]))

            # Create mirror variables for j
            right_of = m.bool(f"right_{i}_{j}")
            below = m.bool(f"below_{i}_{j}")

            m &= (right_of == (left[i] >= right[j]))
            m &= (below == (bottom[i] >= top[j]))

            # At least one of these must be true (containers must be separated)
            m &= (left_of | right_of | above | below)

    # Constraint group 4: separation constraints based on container classes
    for i in range(n_containers):
        for j in range(i + 1, n_containers):
            c_i = classes[i]
            c_j = classes[j]
            sep_ij = separation[c_i][c_j]
            sep_ji = separation[c_j][c_i]
            sep_dist = max(sep_ij, sep_ji)

            if sep_dist > 0:
                # Enforce separation: at least one of these must hold
                # Due to hermax API limitations, we need to be careful with reification
                cond_left = right[i] + sep_dist <= left[j]
                cond_right = left[i] >= right[j] + sep_dist
                cond_above = top[i] + sep_dist <= bottom[j]
                cond_below = bottom[i] >= top[j] + sep_dist

                # Post as direct clause: at least one must be true
                m &= (cond_left | cond_right | cond_above | cond_below)

    return m, {
        "left": left,
        "right": right,
        "top": top,
        "bottom": bottom
    }
