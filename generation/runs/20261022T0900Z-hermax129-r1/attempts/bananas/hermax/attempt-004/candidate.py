from hermax.model import Model


def build(instance):
    # Fixed constants from the description: 5 bananas for $3, 7 oranges for $5,
    # 9 mangoes for $7, 3 apples for $9, 100 fruits for $100, every type at least one.
    # Unit prices scaled by 315 (lcm of 5, 7, 9, 3): banana 189, orange 225, mango 245, apple 945.
    # Budget 100 dollars -> 31500.
    TOTAL = 100
    BUDGET = 31500
    names = ["bananas", "oranges", "mangoes", "apples"]
    price = [189, 225, 245, 945]
    U = TOTAL
    K = U.bit_length()  # bits per quantity, quantities are in 0..U

    m = Model()
    qty = {}
    bits = {}
    for n in names:
        x = m.int(n, 0, U)
        m &= (x >= 1)  # every fruit type is bought at least once
        bv = m.bool_vector(f"{n}_bit", K)
        expr = sum(2 ** k * bv[k] for k in range(K))
        m &= (x == expr)  # channel the integer to bits once
        qty[n] = x
        bits[n] = expr

    # 100 fruits in total.
    m &= (sum(qty[n] for n in names) == TOTAL)
    # Spend exactly 100 dollars, over the bits (cheap weighted equality).
    m &= (sum(price[i] * bits[n] for i, n in enumerate(names)) == BUDGET)

    # Bananas and apples should be as few as possible.
    m.obj += qty["bananas"] + qty["apples"]

    return m, {n: qty[n] for n in names}
