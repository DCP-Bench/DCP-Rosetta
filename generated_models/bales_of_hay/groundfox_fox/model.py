# bales_of_hay: a FOX model for GroundFOX from DCP Rosetta.
#
# You have a number of bales of hay.
#
# For some reason, instead of being weighed individually, they were weighed in all possible
# combinations of two. The weights of each of these combinations were written down and
# arranged in numerical order, without keeping track of which weight matched which pair of
# bales. The weights are given in a list.
#
# Print the weight of each bale (bales) as a list of integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py bales_of_hay.json --check

# bales_of_hay: a FOX model for GroundFOX from DCP Rosetta.

FOX = """
invocabulary { Bale/1 Pair/1 WIdx/1 Val/1 PairOf/3 Wt/2 Sum/3 }
outvocabulary { bales/2 pairw/2 }
theory {
    ! i [Bale(i)] : ? v [Val(v)] : bales(i, v).
    ! i [Bale(i)] : ! v [Val(v)] : ! u [Val(u) & v ~= u] : ~bales(i, v) | ~bales(i, u).
    ! p [Pair(p)] : ? w [WIdx(w)] : pairw(p, w).
    ! p [Pair(p)] : ! w [WIdx(w)] : ! u [WIdx(u) & w ~= u] : ~pairw(p, w) | ~pairw(p, u).
    ! w [WIdx(w)] : ? p [Pair(p)] : pairw(p, w).
    ! w [WIdx(w)] : ! p [Pair(p)] : ! q [Pair(q) & p ~= q] : ~pairw(p, w) | ~pairw(q, w).
    ! p [Pair(p)] : ! w [WIdx(w)] : ! s [Wt(w, s)] : ! i [Bale(i)] : ! j [PairOf(p, i, j)] : ! v [Val(v)] : ! u [Val(u) & ~Sum(v, u, s)] : ~pairw(p, w) | ~bales(i, v) | ~bales(j, u).
}
"""


def structure(instance):
    n = instance["n"]
    weights = instance["weights"]
    m = len(weights)
    top = max(weights) if weights else 0
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    return {
        "Bale": range(n),
        "Pair": range(len(pairs)),
        "WIdx": range(m),
        "Val": range(top + 1),
        "PairOf": [(p, i, j) for p, (i, j) in enumerate(pairs)],
        "Wt": [(w, weights[w]) for w in range(m)],
        "Sum": [(a, b, a + b) for a in range(top + 1) for b in range(top + 1 - a)],
    }
