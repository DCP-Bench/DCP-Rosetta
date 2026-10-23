from hermax.model import Model


def build(instance):
    """Buy 100 fruits for 100 dollars minimizing bananas and apples.

    Costs: 5 bananas = 3 dollars, 7 oranges = 5 dollars,
           9 mangoes = 7 dollars, 3 apples = 9 dollars.
    Total fruits = 100, total cost = 100 dollars.
    All types must be purchased (minimum quantity 1).
    Minimize bananas + apples (not liked).
    """
    model = Model()

    # Variables: quantities of each fruit (constrain bounds based on costs)
    # Max apples: 33 (since 3 apples cost 9 dollars, max 33*3=99 < 100)
    # Max bananas: 166 (since 5 bananas cost 3 dollars, max 166*3/5 = 99.6 < 100)
    # Similar for others
    b = model.int("bananas", 1, 50)
    o = model.int("oranges", 1, 70)
    m = model.int("mangoes", 1, 80)
    a = model.int("apples", 1, 33)

    # Constraint: total fruits = 100
    model &= (b + o + m + a == 100)

    # Constraint: total cost = 100 dollars (in scaled units)
    # 189*b + 225*o + 245*m + 945*a = 31500
    model &= (189 * b + 225 * o + 245 * m + 945 * a == 31500)

    # Objective: minimize bananas + apples (not liked fruits)
    # Use soft clauses on thresholds (unary encoding)
    for i in range(1, 51):  # bananas up to 50
        model.add_soft(b >= i, 1)
    for i in range(1, 34):  # apples up to 33
        model.add_soft(a >= i, 1)

    return model, {"bananas": b, "oranges": o, "mangoes": m, "apples": a}
