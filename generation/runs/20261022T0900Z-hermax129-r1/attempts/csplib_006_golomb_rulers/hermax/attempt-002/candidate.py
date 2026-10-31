import functools
import operator

from hermax.model import Model


def build(instance):
    # Number of marks m comes from the instance.
    size = instance["size"]

    # Upper bound on the length. The optimal length for m marks is at most m*m
    # for the sizes in this problem (for example 55 for m = 10).
    upper = size * size

    model = Model()

    # Marks a_1 .. a_m: a_1 = 0 and the positions strictly increase.
    marks = model.int_vector("mark", size, 0, upper)
    model &= (marks[0] == 0)
    for k in range(size - 1):
        model &= (marks[k] < marks[k + 1])

    # Consecutive gaps are distinct positive integers, so mark k is at least
    # k(k+1)/2 and the suffix after mark k is at least r(r+1)/2 for r = size-1-k.
    # These bounds only narrow the domains; they follow from the definition.
    for k in range(size):
        lo = k * (k + 1) // 2
        r = size - 1 - k
        hi = upper - r * (r + 1) // 2
        model &= (marks[k] >= lo)
        model &= (marks[k] <= hi)

    # Occupancy: occ[p] is true exactly when some mark sits at position p.
    occ = model.bool_vector("occ", upper + 1)
    for k in range(size):
        for p in range(upper + 1):
            model &= (~(marks[k] == p) | occ[p])
    for p in range(upper + 1):
        model &= (~occ[p] | functools.reduce(operator.or_, [marks[k] == p for k in range(size)]))

    # Golomb condition: the m(m-1)/2 differences are distinct. For each distance d,
    # at most one pair of marks may be exactly d apart. pair[d][p] is forced true
    # when positions p and p + d are both occupied.
    for d in range(1, upper + 1):
        pair = model.bool_vector(f"pair_{d}", upper - d + 1)
        for p in range(upper - d + 1):
            model &= (~occ[p] | ~occ[p + d] | pair[p])
        model &= pair.at_most_one()

    # Minimise the length of the ruler, which is the last mark.
    model.obj += marks[size - 1]

    return model, {"length": marks[size - 1], "marks": marks}
