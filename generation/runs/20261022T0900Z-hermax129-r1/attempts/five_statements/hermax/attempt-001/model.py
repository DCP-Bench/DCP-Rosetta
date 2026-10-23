from hermax.model import Model


def build(instance):
    # Five statements problem: determine which statements are true/false.
    # This problem has no instance fields - statements are fixed by the problem.
    # Statement i claims "exactly i of these statements are false"
    # We need to find a consistent assignment.

    m = Model()

    # Decision variables: whether each statement is true (1) or false (0)
    statements = m.bool_vector("statements", 5)

    # Count the number of false statements
    false_count = 5 - sum(statements)

    # Each statement must be consistent with the actual count of false statements:
    # Statement i (1-indexed) is true iff exactly i statements are false
    # statements[i-1] == (false_count == i)

    # This requires reifying each equality into a literal.
    # For each statement i, create a literal that is true iff (false_count == i)
    for i in range(5):
        count_equals_i_plus_1 = (false_count == (i + 1))
        # Statement i must equal this literal
        m &= (statements[i] == count_equals_i_plus_1)

    return m, {
        "statements": statements
    }
