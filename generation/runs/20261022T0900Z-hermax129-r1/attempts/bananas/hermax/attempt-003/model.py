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

    # Variables: quantities of each fruit
    b = model.int("bananas", 1, 100)
    o = model.int("oranges", 1, 100)
    m = model.int("mangoes", 1, 100)
    a = model.int("apples", 1, 100)

    # Constraint: total fruits = 100
    model &= (b + o + m + a == 100)

    # Constraint: total cost = 100 dollars (in scaled units)
    # 189*b + 225*o + 245*m + 945*a = 31500
    model &= (189 * b + 225 * o + 245 * m + 945 * a == 31500)

    # Objective: minimize b + a by charging per unit
    # Since cost equation is expensive, use minimal objective encoding
    model.obj += b + a

    return model, {"bananas": b, "oranges": o, "mangoes": m, "apples": a}
