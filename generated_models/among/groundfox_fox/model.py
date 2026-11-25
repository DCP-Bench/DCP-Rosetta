# among: a FOX model for GroundFOX from DCP Rosetta.
#
# Find an array x of n integers between 0 and 7, inclusive, such that exactly m of them take
# one of the values in v. The other elements may take any other value in that range.
#
# Print the array x (x).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py among.json --check

FOX = """
invocabulary { Pos/1 Val/1 InV/1 Ks/1 Cs/1 Step/2 Succ/2 Last/1 Target/1 }
outvocabulary { x/2 S/2 }
theory {
    ! i [Pos(i)] : ? v [Val(v)] : x(i, v).
    ! i [Pos(i)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~x(i, v) | ~x(i, w).
    ! u [u = 0] : S(0, 0).
    ! k [Ks(k)] : ? c [Cs(c)] : S(k, c).
    ! k [Ks(k)] : ! c [Cs(c)] : ! d [Cs(d) & c ~= d] : ~S(k, c) | ~S(k, d).
    ! k [Ks(k)] : ! k1 [Step(k, k1)] : ! c [Cs(c)] : ! c1 [Succ(c, c1)] : ! v [Val(v) & InV(v)] : ~S(k, c) | ~x(k, v) | S(k1, c1).
    ! k [Ks(k)] : ! k1 [Step(k, k1)] : ! c [Cs(c)] : ! v [Val(v) & ~InV(v)] : ~S(k, c) | ~x(k, v) | S(k1, c).
    ! k [Last(k)] : ! c [Cs(c) & ~Target(c)] : ~S(k, c).
}
"""

FLAGS = []


def structure(instance):
    n = instance["n"]
    m = instance["m"]
    v = instance["v"]
    in_range = sorted({a for a in v if 0 <= a <= 7})
    top = max(n, m, 8) + 2
    return {
        "domain": range(top),
        "Pos": range(n),
        "Ks": range(n + 1),
        "Cs": range(n + 1),
        "Val": range(8),
        "InV": in_range,
        "Step": [(k, k + 1) for k in range(n)],
        "Succ": [(c, c + 1) for c in range(n)],
        "Last": [n],
        "Target": [m],
    }
