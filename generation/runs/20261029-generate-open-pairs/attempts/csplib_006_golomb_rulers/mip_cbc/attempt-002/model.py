# Golomb ruler (CSPLib 006): place `size` marks 0 = a_1 < a_2 < ... < a_m on a ruler so that
# all m(m-1)/2 differences a_j - a_i are distinct, and make the length a_m as small as possible.
import mip


def greedy_ruler(m):
    # The greedy ruler: each next mark is the smallest integer keeping all
    # differences distinct. It is a Golomb ruler, so the optimum is no longer than it,
    # which gives a valid upper bound for every position and difference.
    marks, diffs = [0], set()
    while len(marks) < m:
        v = marks[-1] + 1
        while any((v - a) in diffs for a in marks) or len({v - a for a in marks}) < len(marks):
            v += 1
        diffs.update(v - a for a in marks)
        marks.append(v)
    return marks


def build(instance):
    m = instance["size"]
    greedy = greedy_ruler(m)
    top = greedy[-1]
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    pairs = [(i, j) for i in range(m) for j in range(i + 1, m)]

    # marks[i]: position of mark i on the ruler, the first at 0
    marks = [model.add_var(f"a_{i}", lb=0, ub=top, var_type=mip.INTEGER) for i in range(m)]
    model += marks[0] == 0

    # the marks are strictly increasing; marks i and j enclose j - i + 1 marks whose
    # differences are distinct positive integers, so they lie at least C(j-i+1, 2) apart
    for i, j in pairs:
        k = j - i
        model += marks[j] - marks[i] >= k * (k + 1) // 2

    # each difference a_j - a_i takes exactly one value d, given by a one-hot row of binaries
    diff = {}
    for i, j in pairs:
        k = j - i
        lo = k * (k + 1) // 2
        hi = top - ((m - 1 - k) * (m - k) // 2)
        diff[i, j] = {d: model.add_var(f"d_{i}_{j}_{d}", var_type=mip.BINARY) for d in range(lo, hi + 1)}
        model += mip.xsum(diff[i, j].values()) == 1
        model += marks[j] - marks[i] == mip.xsum(d * b for d, b in diff[i, j].items())

    # all differences are distinct: each value d is the difference of at most one pair
    for d in range(1, top + 1):
        users = [diff[p][d] for p in pairs if d in diff[p]]
        if len(users) > 1:
            model += mip.xsum(users) <= 1

    # the length of the ruler is its last mark, to be minimised
    model.objective = marks[m - 1]

    # start the search from the greedy ruler, a feasible point CBC does not find on its own
    start = [(marks[i], greedy[i]) for i in range(m)]
    for i, j in pairs:
        d = greedy[j] - greedy[i]
        start += [(b, 1 if v == d else 0) for v, b in diff[i, j].items()]
    model.start = start
    return model, {"marks": marks, "length": marks[m - 1]}
