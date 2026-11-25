# csplib_007_all_interval: a FOX model for GroundFOX from DCP Rosetta.
#
# Given the twelve standard pitch-classes (c, c#, d, …), represented by numbers \(0, 1,
# \ldots, 11\), find a series in which each pitch-class occurs exactly once and in which the
# musical intervals between neighbouring notes cover the full set of intervals from the minor
# second (1 semitone) to the major seventh (11 semitones). That is, for each of the intervals,
# there is a pair of neighbouring pitch-classes in the series, between which this interval
# appears.
#
# The problem of finding such a series can be easily formulated as an instance of a more
# general arithmetic problem on \(\mathbb{Z}_n\), the set of integer residues modulo \(n\).
# Given \(n \in \mathbb{N}\), find a vector \(s = (s_1, \ldots, s_n)\), such that
#
# - \(s\) is a permutation of \(\mathbb{Z}_n = \{0, 1, \ldots, n-1\}\); and - the interval
# vector \(v = (|s_2 - s_1|, |s_3 - s_2|, \ldots, |s_n - s_{n-1}|)\) is a permutation of
# \(\mathbb{Z}_n \setminus \{0\} = \{1, 2, \ldots, n-1\}\).
#
# A vector \(v\) satisfying these conditions is called an all-interval series of size \(n\);
# the problem of finding such a series is the all-interval series problem of size \(n\).
#
# Print the sequence of pitch-classes (x) as a list of n integers -between 0 and n-1- and the
# corresponding intervals (diffs) as a list of n-1 integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_007_all_interval.json --check

FOX = """
invocabulary { Pos/1 Val/1 Dp/1 Dl/1 Step/3 Dist/3 }
outvocabulary { x/2 diffs/2 }
theory {
    ! i [Pos(i)] : ? v [Val(v)] : x(i, v).
    ! i [Pos(i)] : ! v [Val(v)] : ! w [Val(w) & ~(v = w)] : ~x(i, v) | ~x(i, w).
    ! v [Val(v)] : ? i [Pos(i)] : x(i, v).
    ! v [Val(v)] : ! i [Pos(i)] : ! j [Pos(j) & ~(i = j)] : ~x(i, v) | ~x(j, v).

    ! k [Dp(k)] : ? d [Dl(d)] : diffs(k, d).
    ! k [Dp(k)] : ! d [Dl(d)] : ! e [Dl(e) & ~(d = e)] : ~diffs(k, d) | ~diffs(k, e).
    ! d [Dl(d)] : ? k [Dp(k)] : diffs(k, d).
    ! d [Dl(d)] : ! k [Dp(k)] : ! l [Dp(l) & ~(k = l)] : ~diffs(k, d) | ~diffs(l, d).

    ! k [Dp(k)] : ! i [Pos(i)] : ! j [Step(k, i, j)] : ! v [Val(v)] : ! w [Val(w)] : ! d [Dist(v, w, d)] : ~x(i, v) | ~x(j, w) | diffs(k, d).
}
"""


def structure(instance):
    n = instance["n"]
    return {
        "Pos": list(range(n)),
        "Val": list(range(n)),
        "Dp": list(range(n - 1)),
        "Dl": list(range(1, n)),
        "Step": [(k, k, k + 1) for k in range(n - 1)],
        "Dist": [(v, w, abs(v - w)) for v in range(n) for w in range(n) if v != w],
    }
