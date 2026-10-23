from hermax.model import Model


def build(instance):
    m = Model()

    # Find a number n between 1 and 10000 where:
    # 1. n + 1 is a perfect square (n + 1 = a^2 for some integer a)
    # 2. n/2 + 1 is a perfect square (n/2 + 1 = b^2 for some integer b)
    # This means n = 2*b^2 - 2 = 2(b^2 - 1)

    # Solve the Pell-like equation a^2 = 2b^2 - 1
    # For each b from 1 to 70, check if 2b^2 - 1 is a perfect square
    # If so, compute n = 2(b^2 - 1) and ensure 1 <= n <= 10000

    n = m.int("n", 1, 10000)

    # Find all valid solutions to a^2 = 2b^2 - 1 with n = 2(b^2 - 1) in range [1, 10000]
    valid_solutions = []
    for b in range(1, 71):
        a_sq = 2 * b * b - 1
        # Check if a_sq is a perfect square
        a = int(a_sq ** 0.5)
        if a * a == a_sq:
            n_val = 2 * (b * b - 1)
            if 1 <= n_val <= 10000:
                valid_solutions.append(n_val)

    # For each valid solution, add a constraint that n can be that value
    # Use disjunction: n must equal at least one of the valid solutions
    disjuncts = [n == sol for sol in valid_solutions]
    if disjuncts:
        m &= sum(disjuncts) >= 1

    return m, {"peculiar": n}
