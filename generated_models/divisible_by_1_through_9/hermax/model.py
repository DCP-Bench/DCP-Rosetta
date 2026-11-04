# divisible_by_1_through_9: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
# Run it (after `pip install hermax`) with:
#   python divisible_by_1_through_9.py

from hermax.model import Model


def create_model(instance):
    """Find a ten-digit number that uses each of the digits 0 to 9 exactly once, and where
    the number formed by its first n digits is divisible by n, for n = 1 to 10."""
    # The problem fixes the number of digits at ten; the instance carries no data.
    n_digits = 10

    m = Model()

    # digit[i] is the i-th digit of the number, counted from the left (digit[0] is the leading digit)
    digit = m.int_vector("digit", n_digits, 0, 9)

    # Each of the digits 0 to 9 is used exactly once.
    m &= digit.all_different()
    # The number has ten digits, so its leading digit must be nonzero. This is already enforced:
    # divisibility by 10 forces digit[9] == 0, and all_different then keeps 0 out of digit[0].

    # The number formed by the first n digits is divisible by n, for every n from 1 to 10.
    # Its value is sum(digit[j] * 10**(n-1-j)). Only its remainder modulo n matters for
    # divisibility, so each power of ten is replaced by its remainder modulo n. The full
    # powers (up to 10**9) make the encoding exceed the evaluator's memory limit; the
    # reduced weights are below n and give the same divisibility. The sum is then an equality
    # with n times a whole-number quotient, which is an auxiliary variable.
    for n in range(1, n_digits + 1):
        weights = [(10 ** (n - 1 - j)) % n for j in range(n)]
        terms = [(w, digit[j]) for j, w in enumerate(weights) if w != 0]
        if not terms:
            continue  # every weight is a multiple of n (always the case for n = 1)
        quotient = m.int(f"quotient_{n}", 0, sum(9 * w for w, _ in terms) // n)
        m &= (sum(w * d for w, d in terms) == n * quotient)

    # This is a satisfaction problem: no objective is posted.
    return m, {"digits": digit}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
