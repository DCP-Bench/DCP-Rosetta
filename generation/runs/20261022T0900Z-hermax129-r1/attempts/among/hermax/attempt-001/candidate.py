from hermax.model import Model


def build(instance):
    n = instance["n"]
    m = instance["m"]
    v = instance["v"]

    m_obj = Model()

    # Create array x of n integers in range [0, n]
    x = m_obj.int_vector("x", n, 0, n)

    # Create a boolean vector to track which elements of x are in v
    in_v = m_obj.bool_vector("in_v", n)

    # For each position, determine if x[i] is in v
    for i in range(n):
        # in_v[i] is true if x[i] is one of the values in v
        # We encode: in_v[i] = 1 iff x[i] in {v[0], v[1], ...}

        # Create equality conditions: x[i] == v[j] for each j
        eq_conditions = [x[i] == v[j] for j in range(len(v))]

        # in_v[i] should be 1 iff at least one condition is true
        # Constraint 1: if x[i] == v[j] for any j, then in_v[i] = 1
        for eq_cond in eq_conditions:
            m_obj &= (eq_cond <= in_v[i])

        # Constraint 2: if in_v[i] = 1, then x[i] must equal some v[j]
        # This is encoded as: in_v[i] <= sum(x[i] == v[j])
        m_obj &= (in_v[i] <= sum(eq_conditions))

    # Exactly m values must be in v
    m_obj &= (sum(in_v) == m)

    return m_obj, {"x": x}
