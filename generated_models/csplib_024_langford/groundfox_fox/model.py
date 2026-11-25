# csplib_024_langford: a FOX model for GroundFOX from DCP Rosetta.
#
# Consider two sets of the numbers from 1 to k. The problem is to arrange the 2k numbers in
# the two sets into a single sequence in which the two 1’s appear one number apart, the two
# 2’s appear two numbers apart, ..., and the two k's appear k numbers apart.
#
# Print the solution sequence (sol) as a list of 2k integers from 1 to k.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_024_langford.json --check

FOX = """
invocabulary { Pos/1 Val/1 Left/2 Far/3 Reach/2 }
outvocabulary { sol/2 First/2 }
theory {
    ! p [Pos(p)] : ? v [Val(v)] : sol(p, v).
    ! p [Pos(p)] : ! v [Val(v)] : ! w [Val(w) & ~(v = w)] : ~sol(p, v) | ~sol(p, w).

    ! v [Val(v)] : ? p [Left(v, p)] : First(v, p).
    ! v [Val(v)] : ! p [Left(v, p)] : ! q [Left(v, q) & ~(p = q)] : ~First(v, p) | ~First(v, q).
    ! v [Val(v)] : ! p [Pos(p) & ~Left(v, p)] : ~First(v, p).
    ! v [Val(v)] : ! p [Left(v, p)] : ~First(v, p) | sol(p, v).
    ! v [Val(v)] : ! p [Left(v, p)] : ! q [Far(v, p, q)] : ~First(v, p) | sol(q, v).
    ! v [Val(v)] : ! p [Reach(v, p)] : ? q [Far(v, q, p)] : First(v, q) | ~sol(p, v) | First(v, p).
    ! v [Val(v)] : ! p [Pos(p) & ~Reach(v, p)] : ~sol(p, v) | First(v, p).
}
"""


def structure(instance):
    k = instance["k"]
    n = 2 * k
    far = [(v, p, p + v + 1) for v in range(1, k + 1) for p in range(n) if p + v + 1 < n]
    return {
        "Pos": list(range(n)),
        "Val": list(range(1, k + 1)),
        "Far": far,
        "Left": [(v, p) for (v, p, _) in far],
        "Reach": [(v, r) for (v, _, r) in far],
    }
