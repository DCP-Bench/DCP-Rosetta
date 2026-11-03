# age_changing: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Run it (after `pip install hermax`) with:
#   python age_changing.py

from hermax.model import Model

# The four operations of the statement, numbered 0..3.
PLUS_2, DIVIDE_BY_8, MINUS_3, TIMES_7 = 0, 1, 2, 3

# The statement fixes no age range. This model assumes both ages are whole
# numbers of years from 0 to 1000, a generous range for two people.
MAX_AGE = 1000
# The smallest value reachable from an age in 0..1000 by these operations is
# -24, and the largest is (1000 + 2) * 7 = 7014.
LOWEST_STEP, HIGHEST_STEP = -100, 7014


def create_model(instance):
    """
    Age changing puzzle. My age m and my husband's age h are whole numbers of
    years. Apply the four operations +2, /8, -3 and *7, each exactly once and in
    some order, to my age: the result is his age. Apply the same four operations,
    each exactly once, in a different order to his age: the result is my age.
    Find both ages.

    The statement fixes every number, so the model ignores the instance (it has
    no fields) and builds the same puzzle every time.
    """
    m = Model()

    # my_age is my age in years (output m)
    my_age = m.int("m", 0, MAX_AGE)
    # husband_age is his age in years (output h)
    husband_age = m.int("h", 0, MAX_AGE)

    # order_to_husband[k] is the operation applied at step k, going from my age to his
    order_to_husband = m.int_vector("order_to_husband", 4, PLUS_2, TIMES_7)
    # order_to_me[k] is the operation applied at step k, going from his age to mine
    order_to_me = m.int_vector("order_to_me", 4, PLUS_2, TIMES_7)

    # from_me[k] is the value after k operations starting from my age
    from_me = m.int_vector("from_me", 5, LOWEST_STEP, HIGHEST_STEP)
    # from_him[k] is the value after k operations starting from his age
    from_him = m.int_vector("from_him", 5, LOWEST_STEP, HIGHEST_STEP)

    # Both chains start and end at the right ages.
    m &= (from_me[0] == my_age)
    m &= (from_me[4] == husband_age)
    m &= (from_him[0] == husband_age)
    m &= (from_him[4] == my_age)

    # Each order uses every operation exactly once.
    m &= order_to_husband.all_different()
    m &= order_to_me.all_different()

    # The two orders are different: at some step they apply different operations.
    # differs[k] is true when the two orders disagree at step k.
    differs = m.bool_vector("differs", 4)
    for k in range(4):
        m &= (order_to_husband[k] != order_to_me[k]).iff(differs[k])
    m &= (differs[0] | differs[1] | differs[2] | differs[3])

    # One step of the chain from my age: the operation chosen at step k turns
    # from_me[k] into from_me[k + 1].
    for k in range(4):
        op = order_to_husband[k]
        before = from_me[k]
        after = from_me[k + 1]
        m &= ((op == PLUS_2).implies(after == before + 2))
        m &= ((op == DIVIDE_BY_8).implies(8 * after == before))  # exact division only
        m &= ((op == MINUS_3).implies(after == before - 3))
        m &= ((op == TIMES_7).implies(after == before * 7))

    # The same, for the chain from his age.
    for k in range(4):
        op = order_to_me[k]
        before = from_him[k]
        after = from_him[k + 1]
        m &= ((op == PLUS_2).implies(after == before + 2))
        m &= ((op == DIVIDE_BY_8).implies(8 * after == before))  # exact division only
        m &= ((op == MINUS_3).implies(after == before - 3))
        m &= ((op == TIMES_7).implies(after == before * 7))

    return m, {"m": my_age, "h": husband_age}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
