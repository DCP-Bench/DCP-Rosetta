# fancy_dress: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Run it (after `pip install hermax`) with:
#   python fancy_dress.py

from hermax.model import Model


def create_model(instance):
    """Mr Greenguest wants to attend a green dress party. Choose which green items to wear
    (a tie, a hat, the shirt he already owns, green socks), or pay the $11 entrance fee if
    he breaks the dress rules, so that the total cost is as small as possible."""
    # The rules and prices are fixed by the problem statement; the instance carries no data.
    tie_price = 10     # buying a green tie costs $10
    hat_price = 2      # a green hat (used) costs $2
    socks_price = 12   # green socks cost $12
    fee = 11           # the entrance fee for a guest not dressed by the rules

    m = Model()
    # t is true when he wears a green tie
    t = m.bool("t")
    # h is true when he wears a green hat
    h = m.bool("h")
    # r is true when he wears the green shirt he owns (it costs nothing)
    r = m.bool("r")
    # s is true when he wears green socks
    s = m.bool("s")
    # n is true when he pays the entrance fee instead of following the rules
    n = m.bool("n")

    # Rule 1: a guest wearing a green tie has to wear a green shirt (unless he pays the fee).
    m &= (~t | r | n)
    # Rule 2: green socks, or a green shirt, only with a green tie or a green hat (unless he pays the fee).
    m &= (~s | t | h | n)
    m &= (~r | t | h | n)
    # Rule 3: a green shirt, or a green hat, or no green socks, requires a green tie (unless he pays the fee).
    m &= (~r | t | n)
    m &= (~h | t | n)
    m &= (s | t | n)

    # Minimise the cost: the tie, hat, socks and fee are paid when worn or paid (the shirt is owned).
    m.obj += tie_price * t
    m.obj += hat_price * h
    m.obj += socks_price * s
    m.obj += fee * n

    return m, {"t": t, "h": h, "r": r, "s": s, "n": n}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
