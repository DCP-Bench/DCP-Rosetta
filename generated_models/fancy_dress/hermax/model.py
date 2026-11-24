# fancy_dress: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Run it (after `pip install hermax`) with:
#   python fancy_dress.py

from hermax.model import Model


def create_model(instance):
    """Mr Greenguest chooses which green items to wear to Mr Greenfan's party, and pays the
    $11 entrance fee if he is not dressed according to rules 1-3, at the lowest total cost.
    He owns a green shirt; a green tie costs $10, a used green hat $2, green socks $12."""
    # The instance has no fields: every number below is from the problem statement.
    m = Model()

    t = m.bool("t")  # he wears a green tie
    h = m.bool("h")  # he wears a green hat
    r = m.bool("r")  # he wears a green shirt
    s = m.bool("s")  # he wears green socks
    n = m.bool("n")  # he pays the entrance fee

    # Rule 4: a guest who is not dressed according to rules 1-3 must pay the fee, so every
    # clause of rules 1-3 below also holds when he pays (n).

    # Rule 1: if someone wears a green tie he has to wear a green shirt.
    m &= (~t | r | n)

    # Rule 2: a guest who wears green socks or a green shirt must also wear a green tie or
    # a green hat: the socks need a tie or a hat, and so does the shirt.
    m &= (~s | t | h | n)
    m &= (~r | t | h | n)

    # Rule 3: a guest wearing a green shirt or a green hat or who does not wear green socks
    # must wear a green tie: the shirt, the hat and bare feet each need the tie.
    m &= (~r | t | n)
    m &= (~h | t | n)
    m &= (s | t | n)

    # Minimise the total cost: the tie, the hat, the socks and the fee (the shirt he owns).
    cost = 10 * t + 2 * h + 12 * s + 11 * n
    m.obj += cost

    # The objective in the problem's terms: the total cost, the cost minimised above.
    return m, {"t": t, "h": h, "r": r, "s": s, "n": n}, cost


if __name__ == "__main__":
    model, outputs, objective = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
