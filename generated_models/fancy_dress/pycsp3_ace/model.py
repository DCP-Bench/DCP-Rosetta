# Fancy dress: Mr Greenguest chooses which green items to wear to Mr Greenfan's party, and
# pays the $11 entrance fee if he is not dressed according to rules 1-3, at the lowest total
# cost. He owns a green shirt; a green tie costs $10, a used green hat $2, green socks $12.

# PyCSP3 star-imports its vocabulary, as every PyCSP3 model does.
# ruff: noqa: F403, F405
from pycsp3 import *

# The instance has no fields: every number below is from the problem statement.
t = Var(dom={0, 1})  # 1 when he wears a green tie
h = Var(dom={0, 1})  # 1 when he wears a green hat
r = Var(dom={0, 1})  # 1 when he wears a green shirt
s = Var(dom={0, 1})  # 1 when he wears green socks
n = Var(dom={0, 1})  # 1 when he pays the entrance fee

satisfy(
    # Rule 4: a guest who is not dressed according to rules 1-3 must pay the fee, so each
    # rule holds or he pays.
    # Rule 1: if someone wears a green tie he has to wear a green shirt.
    Or(imply(t == 1, r == 1), n == 1),
    # Rule 2: a guest who wears green socks or a green shirt must also wear a green tie or
    # a green hat.
    Or(imply(Or(s == 1, r == 1), Or(t == 1, h == 1)), n == 1),
    # Rule 3: a guest wearing a green shirt or a green hat or who does not wear green socks
    # must wear a green tie.
    Or(imply(Or(r == 1, h == 1, s == 0), t == 1), n == 1),
)

# Minimise the total cost: the tie, the hat, the socks and the fee (the shirt he owns).
minimize(10 * t + 2 * h + 12 * s + 11 * n)
