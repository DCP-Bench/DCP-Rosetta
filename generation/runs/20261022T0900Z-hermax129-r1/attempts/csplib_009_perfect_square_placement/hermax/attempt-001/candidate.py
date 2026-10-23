from hermax.model import Model


def build(instance):
    m = Model()

    # Extract instance data
    base = instance["base"]
    sides = instance["sides"]
    n = len(sides)

    # Decision variables: x_coords and y_coords for each square
    x_coords = m.int_vector("x_coords", n, 0, base)
    y_coords = m.int_vector("y_coords", n, 0, base)

    # Constraint 1: Each square must be within the base×base square
    # For each square i: x[i] + side[i] <= base and y[i] + side[i] <= base
    for i in range(n):
        m &= (x_coords[i] + sides[i] <= base)
        m &= (y_coords[i] + sides[i] <= base)

    # Constraint 2: Non-overlap constraints
    # For each pair of squares (i, j) where i < j, at least one of the following must be true:
    # x[i] + side[i] <= x[j]  (i is to the left of j)
    # x[j] + side[j] <= x[i]  (j is to the left of i)
    # y[i] + side[i] <= y[j]  (i is below j)
    # y[j] + side[j] <= y[i]  (j is below i)
    for i in range(n):
        for j in range(i + 1, n):
            # At least one of the four non-overlap conditions must hold
            # We express this as a disjunction using multiple constraints
            left_i_of_j = (x_coords[i] + sides[i] <= x_coords[j])
            right_i_of_j = (x_coords[j] + sides[j] <= x_coords[i])
            below_i_of_j = (y_coords[i] + sides[i] <= y_coords[j])
            above_i_of_j = (y_coords[j] + sides[j] <= y_coords[i])

            # Use binary variables to represent the conditions
            cond_left = m.bool(f"cond_left_{i}_{j}")
            cond_right = m.bool(f"cond_right_{i}_{j}")
            cond_below = m.bool(f"cond_below_{i}_{j}")
            cond_above = m.bool(f"cond_above_{i}_{j}")

            # At least one condition must be true
            m &= (cond_left | cond_right | cond_below | cond_above)

            # Link each condition to the actual constraint
            m &= (cond_left.implies(left_i_of_j))
            m &= (cond_right.implies(right_i_of_j))
            m &= (cond_below.implies(below_i_of_j))
            m &= (cond_above.implies(above_i_of_j))

    return m, {"x_coords": x_coords, "y_coords": y_coords}
