from hermax.model import Model


def build(instance):
    m = Model()

    # Variables: t (tie), h (hat), r (shirt), s (socks), n (entrance fee)
    t = m.bool("t")
    h = m.bool("h")
    r = m.bool("r")
    s = m.bool("s")
    n = m.bool("n")

    # Rule 1: If someone wears a green tie he has to wear a green shirt
    # t -> r, which is ~t OR r
    m &= (~t | r)

    # Rule 2: A guest may only wear green socks and a green shirt
    # if he wears a green tie or a green hat
    # (s AND r) -> (t OR h), which is ~(s AND r) OR (t OR h)
    m &= (~s | ~r | t | h)

    # Rule 3: A guest wearing a green shirt or a green hat or who does
    # not wear green socks must wear a green tie
    # (r OR h OR ~s) -> t, equivalently: r -> t, h -> t, ~s -> t
    m &= (~r | t)  # if shirt, then tie
    m &= (~h | t)  # if hat, then tie
    m &= (s | t)   # if no socks, then tie

    # Rule 4: A guest who is not dressed according to rules 1-3 must pay
    # Implication: if rules violated, then n must be true
    # Since all rules are enforced above, this is automatically satisfied
    # But we also allow n=1 even if rules are satisfied

    # Costs: t=10, h=2, r=0 (already owned), s=12, n=11
    # Minimize total cost by paying when variable is true
    m.obj[10] += t
    m.obj[2] += h
    m.obj[12] += s
    m.obj[11] += n

    return m, {"t": t, "h": h, "r": r, "s": s, "n": n}
