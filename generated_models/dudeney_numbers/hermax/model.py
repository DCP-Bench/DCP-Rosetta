from hermax.model import Model


def build(instance):
    # The number has at most n decimal digits, so it is below 10^n.
    n = instance["n"]
    limit = 10 ** n - 1

    # Largest root c with c^3 <= limit. The number is a cube c^3 with c >= 2,
    # which excludes 1 and keeps the number larger than 1.
    cap = 2
    while (cap + 1) ** 3 <= limit:
        cap += 1

    model = Model()
    root = model.int("root", 2, cap)

    # Digit i of the cube, as a lookup indexed by the root (roots start at 2).
    # These tables only spell out decimal digits of k^3; the search over roots
    # and the digit-sum condition stay in the model.
    digits = model.int_vector("digit", n, 0, 9)
    for i in range(n):
        digit_of_cube = [(k ** 3 // 10 ** i) % 10 for k in range(2, cap + 1)]
        model &= ((digit_of_cube @ root) == digits[i])

    # Dudeney condition: the sum of the digits equals the cube root.
    model &= (sum(digits) == root)

    # The number is the sum of its digits, weighted by powers of ten.
    number = sum(10 ** i * digits[i] for i in range(n))
    return model, {"number": number}
