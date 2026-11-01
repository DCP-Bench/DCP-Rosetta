from hermax.model import Model


def build(instance):
    """
    Sum of all even-valued terms in the Fibonacci sequence not exceeding 4M.

    This problem is purely computational with no instance-specific input.
    Fixed constants: Fibonacci starts with 1, 2; limit is 4,000,000.

    We compute the sequence, collect even terms, and express the result
    as a linear expression of decimal digit variables to stay within memory.
    """
    # Compute the Fibonacci sequence up to the limit
    LIMIT = 4_000_000

    fib = [1, 2]
    while True:
        next_fib = fib[-1] + fib[-2]
        if next_fib > LIMIT:
            break
        fib.append(next_fib)

    # Sum all even-valued terms
    even_sum = sum(f for f in fib if f % 2 == 0)

    # Create hermax model with decimal digit representation
    m = Model()

    # Express the result as a sum of decimal digits
    # even_sum should be around 4.6M, so we need 7 digits maximum
    digits = m.int_vector("digit", 7, 0, 9)

    # Construct the number from its digits: d[0]*10^6 + d[1]*10^5 + ... + d[6]*10^0
    result = sum(10 ** (6 - i) * digits[i] for i in range(7))

    # Constrain the result to equal the computed sum
    m &= (result == even_sum)

    return m, {"res": result}
