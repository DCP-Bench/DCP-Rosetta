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

    # Variables: quantities of each fruit (bounded 1-100)
    b = model.int("bananas", 1, 100)
    o = model.int("oranges", 1, 100)
    m = model.int("mangoes", 1, 100)
    a = model.int("apples", 1, 100)

    # Constraint: total fruits = 100
    model &= (b + o + m + a == 100)

    # Constraint: total cost = 100 dollars
    # Scale by LCM(5,7,9,3)=315 to get integer coefficients
    # (3/5)*b + (5/7)*o + (7/9)*m + (9/3)*a = 100
    # → 189*b + 225*o + 245*m + 945*a = 31500
    model &= (189 * b + 225 * o + 245 * m + 945 * a == 31500)

    # Objective: minimize bananas + apples (not liked fruits)
    # Use soft clauses on threshold constraints to encode the unary sum
    # Each soft clause b >= i charges 1 when satisfied; total cost = banana count
    for i in range(1, 101):
        model.add_soft(b >= i, 1)
        model.add_soft(a >= i, 1)

    return model, {"bananas": b, "oranges": o, "mangoes": m, "apples": a}
