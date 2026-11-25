# session2_subsets_100: a FOX model for GroundFOX from DCP Rosetta.
#
# Out of a set of integers, you are given a list of different integers. From this set A of
# integers you can always find two disjoint non-empty subsets, S and T, such that the sum of
# elements in S equals the sum of elements in T. Note: S union T does not need to be all the
# elements of A. Find sets S and T for the given set A.
#
# Print which elements are in S (in_S) and which elements are in T (in_T), with 2 lists of the
# same length as A, where 1 means that the element is in the subset, and 0 means that it is
# not.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py session2_subsets_100.json --check

# session2_subsets_100: a FOX model for GroundFOX from DCP Rosetta.
#
# Given distinct integers A (n of them), find two disjoint non-empty subsets S and T with equal
# sums. Print in_S and in_T as 0/1 lists of length n.
#
# Each element is in S, in T, or in neither. A layered state st(i, d) says: after the first i
# elements the difference sum(S) - sum(T) is d (shifted by M = sum |A| to be a non-negative
# element). Exactly one state holds per layer (at-least-one clause plus a ladder at-most-one),
# so the state sequence is determined by the choices and cannot start elsewhere. The difference
# is forced forward by data relations AddS/SubT, transitions that leave the range are banned,
# and the final difference must be zero. Non-emptiness of S and T is a plain existential clause.

def _theory():
    return (
        "invocabulary { Elem/1 Layer/1 Last/1 Zero/1 Diff/1 Next/2 Succ/2 AddS/3 SubT/3 OkS/2 OkT/2 }\n"
        "outvocabulary { in_S/2 in_T/2 st/2 seen/2 }\n"
        "theory {\n"
        "    ! i [Elem(i)] : in_S(i, 0) | in_S(i, 1).\n"
        "    ! i [Elem(i)] : ~in_S(i, 0) | ~in_S(i, 1).\n"
        "    ! i [Elem(i)] : in_T(i, 0) | in_T(i, 1).\n"
        "    ! i [Elem(i)] : ~in_T(i, 0) | ~in_T(i, 1).\n"
        "    ! i [Elem(i)] : ~in_S(i, 1) | ~in_T(i, 1).\n"
        "    ? i [Elem(i)] : in_S(i, 1).\n"
        "    ? i [Elem(i)] : in_T(i, 1).\n"
        "    ! d [Zero(d)] : st(0, d).\n"
        "    ! l [Last(l)] : ! d [Zero(d)] : st(l, d).\n"
        "    ! i [Layer(i)] : ? d [Diff(d)] : st(i, d).\n"
        "    ! i [Layer(i)] : ! d [Diff(d)] : ~st(i, d) | seen(i, d).\n"
        "    ! i [Layer(i)] : ! d [Diff(d)] : ! e [Succ(d, e)] : ~seen(i, d) | seen(i, e).\n"
        "    ! i [Layer(i)] : ! d [Diff(d)] : ! e [Succ(d, e)] : ~seen(i, d) | ~st(i, e).\n"
        "    ! i [Elem(i)] : ! j [Next(i, j)] : ! d [Diff(d)] : ~st(i, d) | in_S(i, 1) | in_T(i, 1) | st(j, d).\n"
        "    ! i [Elem(i)] : ! j [Next(i, j)] : ! d [Diff(d)] : ! e [AddS(i, d, e)] : ~st(i, d) | ~in_S(i, 1) | st(j, e).\n"
        "    ! i [Elem(i)] : ! j [Next(i, j)] : ! d [Diff(d)] : ! e [SubT(i, d, e)] : ~st(i, d) | ~in_T(i, 1) | st(j, e).\n"
        "    ! i [Elem(i)] : ! d [Diff(d) & ~OkS(i, d)] : ~st(i, d) | ~in_S(i, 1).\n"
        "    ! i [Elem(i)] : ! d [Diff(d) & ~OkT(i, d)] : ~st(i, d) | ~in_T(i, 1).\n"
        "}\n"
    )


FOX = _theory()


def structure(instance):
    a = instance["A"]
    n = len(a)
    m = sum(abs(x) for x in a)  # every partial difference lies in [-m, m]
    top = 2 * m
    diffs = range(0, top + 1)  # element e stands for difference e - m
    add_s = [(i, d, d + a[i]) for i in range(n) for d in diffs if 0 <= d + a[i] <= top]
    sub_t = [(i, d, d - a[i]) for i in range(n) for d in diffs if 0 <= d - a[i] <= top]
    ok_s = [(i, d) for i in range(n) for d in diffs if 0 <= d + a[i] <= top]
    ok_t = [(i, d) for i in range(n) for d in diffs if 0 <= d - a[i] <= top]
    return {
        "domain": range(0, max(top, n, 3) + 1),
        "Elem": range(n),
        "Layer": range(n + 1),
        "Last": [n],
        "Zero": [m],
        "Diff": list(diffs),
        "Next": [(i, i + 1) for i in range(n)],
        "Succ": [(d, d + 1) for d in range(top)],
        "AddS": add_s,
        "SubT": sub_t,
        "OkS": ok_s,
        "OkT": ok_t,
    }
