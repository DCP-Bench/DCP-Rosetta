# fibonacci_even: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fibonacci_even.html
# Run it (after `pip install hermax`) with:
#   python fibonacci_even.py

from hermax.model import Model, sum_expr

# Problem constants. The statement fixes them, and the instance has no fields.
LIMIT = 4_000_000     # "which do not exceed four million"
FIRST, SECOND = 1, 2  # "By starting with 1 and 2"

# The number of terms of the sequence that do not exceed LIMIT. It is a constant of the
# problem, counted by the same loop the sequence is defined by, so the model has exactly
# one variable per term it must consider.
N_TERMS = 0
a, b = FIRST, SECOND
while a <= LIMIT:
    N_TERMS += 1
    a, b = b, a + b

# Each term is held as decimal digits: a wide integer variable (up to four million) is
# encoded value by value by hermax and runs out of memory, while small digit variables
# with a weighted sum stay cheap. LIMIT has this many decimal digits.
DIGITS = len(str(LIMIT))


def value(digits):
    """The integer written by a list of decimal digits, least significant first."""
    return sum(10**k * digits[k] for k in range(DIGITS))


def create_model(instance):
    """
    Fibonacci even sum: the sum of all even-valued terms in the Fibonacci sequence
    (1, 2, 3, 5, 8, ...) that do not exceed four million.

    The sequence terms are digit variables tied together by the recurrence, so the
    model states the problem's own definition rather than a precomputed list.
    """
    m = Model()

    # term[i][k] is digit k (units = 0) of the (i+1)-th term of the sequence.
    term = [m.int_vector(f"term{i}", DIGITS, 0, 9) for i in range(N_TERMS)]

    # The sequence starts with 1 and 2.
    m &= (value(term[0]) == FIRST)
    m &= (value(term[1]) == SECOND)
    # Each new term is the sum of the two before it, and no term exceeds the limit.
    for i in range(2, N_TERMS):
        m &= (value(term[i]) == value(term[i - 1]) + value(term[i - 2]))
    for i in range(N_TERMS):
        m &= (value(term[i]) <= LIMIT)

    # is_even[i] is true when term i is an even number, which its units digit decides.
    is_even = m.bool_vector("is_even", N_TERMS)
    for i in range(N_TERMS):
        units_parity = m.modulo(term[i][0], 2)  # 0 for an even units digit, 1 for odd
        m &= (units_parity == 0).iff(is_even[i])

    # even_term[i] holds term i's digits when term i is even, and zeros otherwise.
    even_term = [m.int_vector(f"even_term{i}", DIGITS, 0, 9) for i in range(N_TERMS)]
    for i in range(N_TERMS):
        m &= (value(even_term[i]) == value(term[i])).only_if(is_even[i])
        m &= (value(even_term[i]) == 0).only_if(~is_even[i])

    # res: the sum of all the even-valued terms, the answer to the problem.
    res = sum_expr(value(even_term[i]) for i in range(N_TERMS))

    return m, {"res": res}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
