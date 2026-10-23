from hermax.model import Model


def build(instance):
    n = instance["n"]
    max_value = 10 ** n

    # Find all Dudeney numbers with at most n digits and > 1.
    # A Dudeney number is a perfect cube where sum of digits equals the cube root.
    dudeney_numbers = []
    max_root = int((max_value - 1) ** (1/3)) + 1
    for r in range(2, max_root + 1):
        cube = r ** 3
        if cube >= max_value:
            break
        digit_sum = sum(int(d) for d in str(cube))
        if digit_sum == r:
            dudeney_numbers.append(cube)

    m = Model()

    if len(dudeney_numbers) == 0:
        # No solution exists
        m &= False
        number = m.int("number", 0, 0)
    else:
        # Create a binary variable for each Dudeney number.
        # Exactly one is chosen, and the output is the selected number.
        is_chosen = m.bool_vector("is_chosen", len(dudeney_numbers))
        m &= (sum(is_chosen) == 1)
        number = sum(dudeney_numbers[i] * is_chosen[i] for i in range(len(dudeney_numbers)))

    return m, {"number": number}
