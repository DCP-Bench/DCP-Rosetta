# age_changing: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python age_changing.py

from pycsp3 import *


def create_model(instance):
    """Start with my age and apply the four operations +2, /8, -3 and *7, each once,
    in some order: the result is my husband's age. Start with his age and apply the
    same four operations in a different order: the result is my age. Both ages are
    between 16 and 120, every intermediate result is a positive integer and a division
    by 8 must be exact. Find my age and my husband's age."""
    # both ages are between 16 and 120 (the statement)
    min_age = 16
    max_age = 120

    # The four operations, each used once in a calculation.
    n_operations = 4
    PLUS_2, DIVIDE_BY_8, MINUS_3, TIMES_7 = range(n_operations)

    # The largest intermediate value: the largest age plus 2, then times 7. Each operation
    # is used once, so *7 is the only growing step; no other order gives a larger value.
    max_value = (max_age + 2) * 7
    intermediate_values = range(1, max_value + 1)

    # Each row is (operation, value before, value after); a result must be a positive
    # integer, so -3 needs at least 4 and /8 needs an exact division.
    transitions = (
        [(PLUS_2, x, x + 2) for x in intermediate_values if x + 2 <= max_value]
        + [(DIVIDE_BY_8, x, x // 8) for x in intermediate_values if x % 8 == 0]
        + [(MINUS_3, x, x - 3) for x in intermediate_values if x - 3 >= 1]
        + [(TIMES_7, x, 7 * x) for x in intermediate_values if 7 * x <= max_value]
    )

    # My age and my husband's age, the two answers.
    my_age = Var(dom=range(min_age, max_age + 1))
    husband_age = Var(dom=range(min_age, max_age + 1))

    # The order of the operations in the first calculation (from my age to his):
    # order_1[k] is the operation applied at step k. The second calculation (from his age
    # back to mine) has its own order, order_2.
    order_1 = VarArray(size=n_operations, dom=range(n_operations))
    order_2 = VarArray(size=n_operations, dom=range(n_operations))

    # The values along each calculation: chain_1[0] is my age, chain_1[n_operations] is his age;
    # chain_2[0] is his age, chain_2[n_operations] is my age.
    chain_1 = VarArray(size=n_operations + 1, dom=intermediate_values)
    chain_2 = VarArray(size=n_operations + 1, dom=intermediate_values)

    satisfy(
        # Each of the four operations is used exactly once in each calculation.
        AllDifferent(order_1),
        AllDifferent(order_2),
        # The second calculation uses a different order from the first.
        Hamming(order_1, order_2) >= 1,
        # Starting from my age gives my husband's age.
        chain_1[0] == my_age,
        chain_1[n_operations] == husband_age,
        # Starting from his age gives my age.
        chain_2[0] == husband_age,
        chain_2[n_operations] == my_age,
        # Each step of each calculation applies its operation to the previous value.
        [Table(scope=[order_1[k], chain_1[k], chain_1[k + 1]], supports=transitions) for k in range(n_operations)],
        [Table(scope=[order_2[k], chain_2[k], chain_2[k + 1]], supports=transitions) for k in range(n_operations)],
    )

    return {"m": my_age, "h": husband_age}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
