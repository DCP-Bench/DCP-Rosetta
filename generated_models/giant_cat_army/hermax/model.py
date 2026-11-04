# giant_cat_army: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
# Run it (after `pip install hermax`) with:
#   python giant_cat_army.py

from hermax.model import Model


def create_model(instance):
    """Giant cat army: start from the list [0] and build a list of 24 integers.
    Each step adds 5, adds 7, or takes the square root of the current number (only
    when it is a perfect square). The numbers must be distinct integers between 0 and 60,
    the list must end with 14, and it must contain 2, 10 and 14 in that order
    (other numbers may lie between them).

    The instance has no fields: the statement fixes every number used here.
    """
    # The list has exactly 24 numbers, x[0] to x[23]: fixed by the statement.
    n = 24
    # Every number in the list is at most 60: fixed by the statement.
    largest = 60

    m = Model()

    # x[k] is the k-th number of the list, an integer from 0 to 60
    x = m.int_vector("x", n, 0, largest)

    # The list starts with 0 and ends with 14.
    m &= (x[0] == 0)
    m &= (x[n - 1] == 14)

    # All numbers in the list are distinct.
    m &= x.all_different()

    for k in range(n - 1):
        # op[j] is true when step k uses operation j: 0 adds 5, 1 adds 7, 2 takes the square root.
        op = m.bool_vector(f"op_{k}", 3)

        # Each step uses exactly one of the three operations.
        m &= op.exactly_one()

        # Adding 5: the next number is the current number plus 5.
        m &= (x[k + 1] == x[k] + 5).only_if(op[0])
        # Adding 7: the next number is the current number plus 7.
        m &= (x[k + 1] == x[k] + 7).only_if(op[1])
        # Square root: the current number is the square of the next number,
        # so the next number is its root. The square of x[k + 1] is written as a
        # step function over its values, since hermax has no product of two integers.
        square_of_next = x[k + 1].piecewise(
            base_value=0, steps={t: t * t for t in range(1, largest + 1)})
        m &= (x[k] == square_of_next).only_if(op[2])

    # position_2, position_10, position_14 are where 2, 10 and 14 sit in the list.
    position_2 = m.int("position_2", 0, n - 1)
    position_10 = m.int("position_10", 0, n - 1)
    position_14 = m.int("position_14", 0, n - 1)

    # The list holds 2, 10 and 14 at those positions.
    m &= (x[position_2] == 2)
    m &= (x[position_10] == 10)
    m &= (x[position_14] == 14)

    # They appear in that order: 2, then 10, then 14.
    m &= (position_2 < position_10)
    m &= (position_10 < position_14)

    # The statement asks for no cost: the model is a satisfaction problem.
    return m, {"x": x}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
