from hermax.model import Model


def build(instance):
    n = instance["n"]
    m = instance["m"]
    v = instance["v"]

    m_obj = Model()

    # Create array x of n integers in range [0, n]
    x = m_obj.int_vector("x", n, 0, n)

    # Count how many positions have a value from v
    # For each position i, x[i] is in v if x[i] equals some value in v
    # We can express this as: for each position, create a boolean that is 1 iff x[i] in v

    # Create auxiliary boolean variables
    in_v_indicators = m_obj.bool_vector("in_v", n)

    # For each position i
    for i in range(n):
        # in_v_indicators[i] should be 1 iff x[i] is one of the values in v
        # Create a big disjunction: x[i] == v[0] OR x[i] == v[1] OR ...

        # In hermax MaxSAT, we can express this by creating soft clauses
        # If x[i] is in v, the indicator is 1
        # If x[i] is not in v, the indicator is 0

        # We need: indicator[i] = 1 iff (x[i] in v)
        # Which means: indicator[i] = 1 iff (x[i] == v[0] or x[i] == v[1] or ...)

        # For each value in v, if x[i] equals it, indicator must be 1
        for v_val in v:
            # If x[i] == v_val, then in_v_indicators[i] must be 1
            # This is: (x[i] != v_val) OR in_v_indicators[i]
            m_obj &= ((x[i] != v_val) | in_v_indicators[i])

        # Also, if in_v_indicators[i] == 1, then x[i] must be one of the values
        # This is: in_v_indicators[i] => (x[i] in v)
        # Which is: NOT in_v_indicators[i] OR (x[i] == v[0] OR ... OR x[i] == v[len(v)-1])
        # Or equivalently: in_v_indicators[i] <= max(x[i] == v_val for v_val in v)
        # We can encode this using a disjunction

        # Create the "at least one value matches" constraint
        value_matches = [x[i] == v_val for v_val in v]
        # If indicator is 1, at least one must match
        # Constraint: in_v_indicators[i] <= sum(value_matches)
        # But we can't directly use <= with Literals

        # Instead: ~in_v_indicators[i] OR (x[i] == v[0] OR x[i] == v[1] OR ...)
        # This is: NOT in_v_indicators[i] OR OR(value_matches)
        or_clause = value_matches[0]
        for vm in value_matches[1:]:
            or_clause = or_clause | vm
        m_obj &= (~in_v_indicators[i] | or_clause)

    # Exactly m values must be in v
    m_obj &= (sum(in_v_indicators) == m)

    return m_obj, {"x": x}
