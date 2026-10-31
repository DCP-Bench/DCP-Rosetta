from hermax.model import Model


def build(instance):
    n = instance["n"]
    m = instance["m"]

    # Series S has n+2 elements indexed 0 to n+1
    # S[i] = count of occurrences of value i in S, for i from 0 to n
    # S[n+1] = m
    series_len = n + 2

    model = Model()

    # Create the series as integer variables (0 to series_len-1)
    series = model.int_vector("series", series_len, 0, series_len - 1)

    # Constraint: S[n+1] = m
    model &= (series[n + 1] == m)

    # Constraint: sum of all series elements = series_len
    # (because each count adds up to the total length)
    model &= (sum(series[i] for i in range(series_len)) == series_len)

    # Self-describing constraints: for each value i from 0 to n,
    # count of i in series must equal series[i]
    for i in range(n + 1):
        # Count occurrences of value i in series
        # Use auxiliary boolean variables
        is_i_var = model.bool_vector(f"is_{i}", series_len)

        # Link each boolean to the corresponding series element
        for j in range(series_len):
            # is_i_var[j] = True iff series[j] == i
            # In hermax, we need to use appropriate constraints
            # We can't directly assign a boolean to an equality, but we can
            # use the fact that hermax accepts linear constraints
            # For now, let's try a simpler approach
            pass

        # Actually, let's use a different strategy:
        # Create auxiliary integer variables for each value at each position
        # and use that to count
        pass

    # Alternative: enumerate all possible values at each position
    # This is similar to attempt-001 but might be cleaner

    # For each position j, we need it to have exactly one value
    # Create decision variables: pos_val[j][v] = True if series[j] = v
    pos_val = []
    for j in range(series_len):
        is_value = model.bool_vector(f"pv_{j}", series_len)
        pos_val.append(is_value)

        # Exactly one value per position
        model &= is_value.exactly_one()

        # Set series[j] to the value indicated
        # series[j] = sum(v * is_value[v] for v in range(series_len))
        model &= (series[j] == sum(v * is_value[v] for v in range(series_len)))

    # Constraint: S[n+1] = m (second constraint for clarity)
    model &= (series[n + 1] == m)

    # Self-describing property
    for i in range(n + 1):
        # Count how many positions have value i
        count_i = model.sum_var([pos_val[j][i] for j in range(series_len)])
        # This must equal series[i]
        model &= (count_i == series[i])

    return model, {"s": series}
