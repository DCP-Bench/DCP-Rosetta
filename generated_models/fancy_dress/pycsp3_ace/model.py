# fancy_dress: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python fancy_dress.py

from pycsp3 import *


def create_model(instance):
    """Mr. Greenfan's dress party requires green dresses from the male guests. A guest
    who wears a green tie must wear a green shirt. A guest who wears green socks or a
    green shirt must wear a green tie or a green hat. A guest who wears a green shirt,
    a green hat, or does not wear green socks must wear a green tie. A guest who is not
    dressed according to these rules pays an 11 entrance fee. Mr Greenguest owns a green
    shirt; a green tie costs 10, a green hat 2 and green socks 12. Find the cheapest
    choice of tie, hat, shirt, socks and entrance fee for him to take part."""
    tie_cost = 10  # the price of a green tie
    hat_cost = 2  # the price of a used green hat
    socks_cost = 12  # the price of green socks
    entrance_fee = 11  # the fee for a guest not dressed according to the rules

    # tie is 1 when the guest wears a green tie
    tie = Var(dom={0, 1})
    # hat is 1 when the guest wears a green hat
    hat = Var(dom={0, 1})
    # shirt is 1 when the guest wears a green shirt; he owns one, so wearing it costs nothing
    shirt = Var(dom={0, 1})
    # socks is 1 when the guest wears green socks
    socks = Var(dom={0, 1})
    # fee is 1 when the guest pays the entrance fee
    fee = Var(dom={0, 1})

    # Rule 1: a guest who wears a green tie has to wear a green shirt.
    rule_1 = imply(tie == 1, shirt == 1)
    # Rule 2: a guest who wears green socks or a green shirt has to wear a green tie or a green hat.
    rule_2 = imply(Or(socks == 1, shirt == 1), Or(tie == 1, hat == 1))
    # Rule 3: a guest who wears a green shirt, a green hat or no green socks has to wear a green tie.
    rule_3 = imply(Or(shirt == 1, hat == 1, socks == 0), tie == 1)

    satisfy(
        # A guest who breaks one of rules 1 to 3 pays the entrance fee.
        Or(fee == 1, And(rule_1, rule_2, rule_3)),
    )

    # The cost of the choices: the tie, the hat, the socks and the entrance fee.
    minimize(tie_cost * tie + hat_cost * hat + socks_cost * socks + entrance_fee * fee)

    # The output keys are the single letters of the problem: t, h, r, s and n.
    return {"h": hat, "n": fee, "r": shirt, "s": socks, "t": tie}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is OPTIMUM:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
