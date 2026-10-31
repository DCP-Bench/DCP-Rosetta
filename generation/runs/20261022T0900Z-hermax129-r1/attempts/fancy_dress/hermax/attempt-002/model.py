from hermax.model import Model


def build(instance):
    m = Model()
    t = m.bool("t")  # green tie, costs 10
    h = m.bool("h")  # green hat (used), costs 2
    r = m.bool("r")  # green shirt, already owned, costs nothing
    s = m.bool("s")  # green socks, cost 12
    n = m.bool("n")  # entrance fee of 11

    # The fee is paid whenever a rule is broken. Each clause says: the rule
    # holds, or the fee is paid. The minimiser only sets n when needed.

    # Rule 1: a green tie requires a green shirt.
    m &= (~t | r | n)

    # Rule 2: green socks and a green shirt require a green tie or a green hat.
    m &= (~s | ~r | t | h | n)

    # Rule 3: a green shirt, a green hat, or no green socks requires a green tie.
    m &= (~r | t | n)
    m &= (~h | t | n)
    m &= (s | t | n)

    # Mr Greenguest wears the green shirt he owns (otherwise the fee would be $9).
    m &= r

    # Cost of the choices. The shirt is owned, so it adds nothing.
    m.obj += 10 * t + 2 * h + 12 * s + 11 * n

    return m, {"t": t, "h": h, "r": r, "s": s, "n": n}
