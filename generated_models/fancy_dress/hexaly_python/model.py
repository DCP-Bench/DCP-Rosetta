"""Fancy dress: Mr Greenguest chooses which green items to wear to Mr Greenfan's party, and pays
the $11 entrance fee if he is not dressed according to rules 1-3, at the lowest total cost. He owns
a green shirt; a green tie costs $10, a used green hat $2, green socks $12."""
import hexaly.optimizer as hx


def build(instance):
    # The instance has no fields: every number below is from the problem statement.
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    tie = model.bool()    # he wears a green tie
    hat = model.bool()    # he wears a green hat
    shirt = model.bool()  # he wears a green shirt
    socks = model.bool()  # he wears green socks
    fee = model.bool()    # he pays the entrance fee

    # Rule 4: a guest who is not dressed according to rules 1-3 must pay the fee. Each rule
    # below is written as "what it asks for, or the fee": item <= wanted + fee says that
    # wearing the item needs one of the wanted items, unless he pays. Linear rows over
    # Booleans give Hexaly the bounds that prove the optimum.

    # Rule 1: if someone wears a green tie he has to wear a green shirt.
    model.constraint(tie <= shirt + fee)

    # Rule 2: a guest who wears green socks or a green shirt must also wear a green tie or a
    # green hat: the socks need a tie or a hat, and so does the shirt.
    model.constraint(socks <= tie + hat + fee)
    model.constraint(shirt <= tie + hat + fee)

    # Rule 3: a guest wearing a green shirt or a green hat or who does not wear green socks
    # must wear a green tie: the shirt, the hat and bare feet (1 - socks) each need the tie.
    model.constraint(shirt <= tie + fee)
    model.constraint(hat <= tie + fee)
    model.constraint(1 - socks <= tie + fee)

    # Minimise the total cost: the tie, the hat, the socks and the fee (the shirt he owns).
    model.minimize(10 * tie + 2 * hat + 12 * socks + 11 * fee)

    return optimizer, {"t": tie, "h": hat, "r": shirt, "s": socks, "n": fee}
