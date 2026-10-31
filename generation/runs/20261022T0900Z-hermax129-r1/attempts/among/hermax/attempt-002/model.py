from hermax.model import Model


def build(instance):
    n = instance["n"]
    m = instance["m"]
    v = instance["v"]

    m_obj = Model()

    # Create array x of n integers in range [0, n]
    x = m_obj.int_vector("x", n, 0, n)

    # Among constraint: exactly m values in x are from the set v
    # Approach: count the sum of (x[i] == v[j]) for all i, j
    # This count should equal m

    # Create a matrix of boolean variables: appears[i][j] = 1 iff x[i] == v[j]
    count = 0
    for i in range(n):
        for j in range(len(v)):
            # For each position i and each value v[j],
            # check if x[i] == v[j]
            # This equality is a Literal that we can sum
            eq = x[i] == v[j]
            # Add this to the count
            # eq is a Literal (boolean expression) in hermax
            # We can directly sum Literals
            count += eq

    # Exactly m values must be from v
    m_obj &= (count == m)

    return m_obj, {"x": x}
