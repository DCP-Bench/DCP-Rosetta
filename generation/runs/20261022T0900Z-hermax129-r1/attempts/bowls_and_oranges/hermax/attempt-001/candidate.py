from hermax.model import Model


def build(instance):
    """
    Place m oranges in n bowls (numbered 1 to n) such that no three
    oranges form an arithmetic progression in their positions.

    Constraint: no three oranges at positions A, B, C where B - A = C - B.
    Output: array of m bowl positions (1-indexed), padded to 9 integers.
    """
    n = instance["n"]  # number of bowls
    m = instance["m"]  # number of oranges

    model = Model()

    # Create output variables for positions (these are the main decision variables)
    output_pos = model.int_vector("pos", m, 1, n)

    # All positions must be distinct
    model &= output_pos.all_different()

    # All positions must be in ascending order
    model &= output_pos.increasing()

    # Constraint: no arithmetic progression among the selected positions
    # For all triples (i, j, k) in [0, m-1] where i < j < k,
    # ensure that output_pos[j] - output_pos[i] != output_pos[k] - output_pos[j]
    # i.e., the positions are not in arithmetic progression

    for i in range(m):
        for j in range(i + 1, m):
            for k in range(j + 1, m):
                # output_pos[i], output_pos[j], output_pos[k] must not form AP
                # i.e., 2*output_pos[j] != output_pos[i] + output_pos[k]
                model &= (2 * output_pos[j] != output_pos[i] + output_pos[k])

    # Pad output to 9 elements
    output_array = model.int_vector("output", 9, 0, n)
    for i in range(m):
        model &= (output_array[i] == output_pos[i])
    for i in range(m, 9):
        model &= (output_array[i] == 0)

    return model, {"x": output_array}
