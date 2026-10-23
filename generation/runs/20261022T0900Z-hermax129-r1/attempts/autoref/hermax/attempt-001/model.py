from hermax.model import Model


def build(instance):
    n = instance["n"]
    m = instance["m"]

    # The series S has n+2 elements: (s0, s1, ..., sn, s(n+1))
    # The series is self-describing: s[i] is the count of value i in S
    # and s[n+1] = m.
    series_len = n + 2

    model = Model()

    # Create the series as integer variables
    # Each series[j] can be a value from 0 to series_len-1
    series = model.int_vector("series", series_len, 0, series_len - 1)

    # Constraint: series[n+1] = m
    model &= (series[n + 1] == m)

    # Self-describing property: for each value i from 0 to n,
    # the count of i in the series must equal series[i]
    for i in range(n + 1):
        # Count how many positions in the series have value i
        # We need to count: sum(1 if series[j] == i else 0 for j in range(series_len))
        # This requires creating auxiliary boolean variables for each position
        indicators = model.bool_vector(f"count_{i}", series_len)

        # Link each indicator to whether series[j] == i
        for j in range(series_len):
            # indicators[j] is True iff series[j] == i
            # We can't directly express this in MaxSAT, so we use a different approach
            # We'll post the constraint as a linear combination
            # Actually, let me use a different approach: enumerate all values
            pass

    # Alternative approach: for each position, enumerate which value it takes
    # and ensure the self-referential constraints are met

    # For each position j and value v, create a binary variable indicating series[j] = v
    position_is_value = []
    for j in range(series_len):
        is_value_list = model.bool_vector(f"pos_{j}_val", series_len)
        position_is_value.append(is_value_list)

        # Exactly one value per position
        model &= is_value_list.exactly_one()

        # The series value equals the weighted sum of the indicators
        value_expr = sum(v * is_value_list[v] for v in range(series_len))
        model &= (series[j] == value_expr)

    # Self-describing property
    for i in range(n + 1):
        # Count occurrences of value i
        count_i = model.sum_var([position_is_value[j][i] for j in range(series_len)])
        # This must equal series[i]
        model &= (count_i == series[i])

    return model, {"s": series}
