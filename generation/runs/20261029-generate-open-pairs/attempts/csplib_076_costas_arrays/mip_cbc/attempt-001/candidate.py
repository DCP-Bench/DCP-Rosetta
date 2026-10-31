# Costas arrays (CSPLib 076): place n marks on an n x n grid, one per row and one per column,
# so that all n(n-1)/2 vectors between marks differ. Equivalently, X_1..X_n is a permutation
# and, for every lag l, the differences X_{i+l} - X_i along row l of the difference triangle
# are all different. Output: X_1..X_n with values 1..n.
import mip


def build(instance):
    n = instance["n"]
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    values = range(1, n + 1)

    # at[i][v - 1] = 1 when X_i = v
    at = [[model.add_var(f"at_{i}_{v}", var_type=mip.BINARY) for v in values] for i in range(n)]
    # X is a permutation: one value per position, and each value used once
    for i in range(n):
        model += mip.xsum(at[i]) == 1
    for k in range(n):
        model += mip.xsum(at[i][k] for i in range(n)) == 1

    # Row l of the difference triangle holds X_{i+l} - X_i for every i. For each lag l and each
    # difference d, gap[i] (continuous in [0, 1]) is pushed to 1 when X_i = v and X_{i+l} = v + d
    # for some v; at most one i may have difference d, so these indicators sum to at most 1.
    # The pushing rows are all that is needed: nothing forces an indicator up without its pair.
    for l in range(1, n):
        for d in range(-(n - 1), n):
            if d == 0:
                continue   # X is a permutation, so no difference is 0
            starts = [i for i in range(n - l)]
            gap = {}
            for i in starts:
                pairs = [(v, v + d) for v in values if 1 <= v + d <= n]
                if not pairs:
                    continue
                gap[i] = model.add_var(f"gap_{l}_{d}_{i}", lb=0, ub=1)
                for v, w in pairs:
                    model += gap[i] >= at[i][v - 1] + at[i + l][w - 1] - 1
            # each difference appears at most once in row l of the triangle
            if len(gap) > 1:
                model += mip.xsum(gap.values()) <= 1

    costas = []
    for i in range(n):
        x = model.add_var(f"X_{i}", lb=1, ub=n, var_type=mip.INTEGER)
        model += x == mip.xsum(v * at[i][v - 1] for v in values)
        costas.append(x)
    return model, {"costas": costas}
