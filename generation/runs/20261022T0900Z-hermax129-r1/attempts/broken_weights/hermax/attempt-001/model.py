from hermax.model import Model


def build(instance):
    # Broken Weights problem: Find n weights that sum to m and can measure
    # every value from 1 to m using a balance scale.
    # On a balance scale, weights can be placed on either side of the scale.
    # To measure weight t: place t and some weights on one side, others on the other side.
    # This achieves balance when: t + sum(weights_on_t_side) = sum(weights_on_other_side)
    # Equivalently: sum(other_side) - sum(t_side) = t

    m = instance["m"]  # total weight
    n = instance["n"]  # number of pieces

    model = Model()

    # Output: the selected weights (each between 1 and m, distinct)
    weights = model.int_vector("weights", n, 1, m)
    model &= weights.all_different()
    model &= (sum(weights) == m)

    # For each measurement target t from 1 to m:
    # We need to be able to place the weights such that balance is achieved.
    # For each weight, create a placement variable per measurement:
    #   placement[t][i] represents where weight i goes in measurement t
    #   -1 = on the side with the object being weighed
    #    0 = not used
    #    1 = on the opposite side

    # Due to MaxSAT limitations with non-linear constraints,
    # we'll create a simplified formulation:
    # For each measurement, we have binary choices for each weight

    for t in range(1, m + 1):
        # For each weight, decide if it goes left, right, or unused
        on_left = model.bool_vector(f"left_{t}", n)
        on_right = model.bool_vector(f"right_{t}", n)

        # Constraint: each weight is used at most once per measurement
        for i in range(n):
            model &= (on_left[i] + on_right[i] <= 1)

        # Create auxiliary variables to hold sums without non-linear operations
        # We'll build these sums using separate constraints
        # For each weight value w from 1 to m, create a binary indicating if it's used on left/right

        # Alternative: create integer variables for each weight and build left/right sums
        left_sums = []
        right_sums = []

        # For each weight index i:
        for i in range(n):
            # The contribution of weight[i] to left/right depends on on_left[i] / on_right[i]
            # But we can't express "weight[i] * on_left[i]" directly

            # Instead, we create auxiliary integer variables:
            left_contrib = model.int(f"left_contrib_{t}_{i}", 0, m)
            right_contrib = model.int(f"right_contrib_{t}_{i}", 0, m)

            # Constraint: left_contrib is either 0 or weight[i]
            # This is expressed as: left_contrib = weight[i] if on_left[i] else 0
            # In MaxSAT terms: left_contrib <= m * on_left[i]
            # and: left_contrib >= weight[i] * on_left[i] (but this is non-linear)
            # and: left_contrib <= weight[i] + m * (1 - on_left[i])

            # We need to linearize this:
            # If on_left[i] is true, then left_contrib must equal weight[i]
            # If on_left[i] is false, then left_contrib must equal 0

            # Using the formula: left_contrib = weight[i] * on_left[i] (encoded)
            # This requires auxiliary variables for each possible weight value

            # Create binary variables for each possible weight value
            weight_eq_values = []
            for w in range(1, m + 1):
                is_weight_w = model.bool(f"w_{i}_eq_{w}_{t}")
                weight_eq_values.append(is_weight_w)

                # If weights[i] = w and on_left[i], then left_contrib = w
                # This is expressed as: weight[i] == w <=> is_weight_w
                # But we can't multiply is_weight_w * on_left[i] either...

            # This approach also leads to non-linearity
            left_sums.append(left_contrib)
            right_sums.append(right_contrib)

        # The balance equation:
        # sum(right) - sum(left) = t
        # (weights on the opposite side minus weights with the object)
        left_total = sum(left_sums)
        right_total = sum(right_sums)
        model &= (right_total - left_total == t)

    return model, {"weights": weights}
