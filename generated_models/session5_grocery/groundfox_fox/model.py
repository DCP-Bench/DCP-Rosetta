# session5_grocery: a FOX model for GroundFOX from DCP Rosetta.
#
# A kid goes into a grocery store and buys a number of items. The cashier charges a total
# price, the kid pays and is about to leave when the cashier calls the kid back, and says
# "Hold on, I multiplied the items instead of adding them; I’ll try again; Hah, with adding
# them the price still comes to the same total price". What were the prices of the items?
#
# Each price is a positive whole number of cents, and `total_price` is given in cents. Both
# the sum and the product of the prices in dollars equal the total price in dollars.
#
# Print the prices of the items (prices) in cents, as a list of integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py session5_grocery.json --check

from math import isqrt

# Both sum and product of the prices (in dollars) equal the total (in dollars):
#   sum(prices) = total_price (cents)
#   prod(prices) = total_price * 100**(n-1)   (cents, n items)
# Every price divides D = prod, and every price is at most total_price.
# Partial sums and partial products are tracked as layers over the items; a value
# that overflows its bound moves to an absorbing overflow element that the final
# layer forbids, so no partial state can silently disappear from the chain.

FOX = """
invocabulary { Item/1 Layer/1 Last/1 Nxt/2 Val/1 Sum/1 Target/1 Add/3 Prod/1 TargetP/1 Mul/3 }
outvocabulary { prices/2 S/2 Q/2 }
theory {
    ! i [Item(i)] : ? v [Val(v)] : prices(i, v).
    ! i [Item(i)] : ! v [Val(v)] : ! w [Val(w) & ~(v = w)] : ~prices(i, v) | ~prices(i, w).

    ! u [u = 0] : S(0, 0).
    ! u [u = 0] : Q(0, 1).
    ! i [Item(i)] : ! j [Nxt(i, j)] : ! s [Sum(s)] : ! v [Val(v)] : ! t [Add(s, v, t)] : ~S(i, s) | ~prices(i, v) | S(j, t).
    ! i [Item(i)] : ! j [Nxt(i, j)] : ! m [Prod(m)] : ! v [Val(v)] : ! t [Mul(m, v, t)] : ~Q(i, m) | ~prices(i, v) | Q(j, t).

    ! l [Last(l)] : ! s [Target(s)] : S(l, s).
    ! l [Last(l)] : ! s [Sum(s) & ~Target(s)] : ~S(l, s).
    ! l [Last(l)] : ! m [TargetP(m)] : Q(l, m).
    ! l [Last(l)] : ! m [Prod(m) & ~TargetP(m)] : ~Q(l, m).
}
"""


def _divisors(x):
    small, large = [], []
    for d in range(1, isqrt(x) + 1):
        if x % d == 0:
            small.append(d)
            if d != x // d:
                large.append(x // d)
    return sorted(small + large)


def structure(instance):
    n = instance["num_items"]
    total = instance["total_price"]
    target = total * 100 ** (n - 1)
    sum_over = total + 1          # absorbing overflow for partial sums
    prod_over = target + 1        # absorbing overflow for partial products
    val = [d for d in _divisors(target) if d <= total]
    prod = _divisors(target) + [prod_over]
    add = []
    for s in range(total + 2):
        for v in val:
            t = s + v if s <= total and s + v <= total else sum_over
            add.append((s, v, t))
    mul = []
    for m in prod:
        for v in val:
            if m == prod_over:
                t = prod_over
            else:
                t = m * v if target % (m * v) == 0 else prod_over
            mul.append((m, v, t))
    return {
        "Item": list(range(n)),
        "Layer": list(range(n + 1)),
        "Last": [n],
        "Nxt": [(i, i + 1) for i in range(n)],
        "Val": val,
        "Sum": list(range(total + 2)),
        "Target": [total],
        "Add": add,
        "Prod": prod,
        "TargetP": [target],
        "Mul": mul,
    }
