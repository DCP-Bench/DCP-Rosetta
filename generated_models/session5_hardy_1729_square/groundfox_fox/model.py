# session5_hardy_1729_square: a FOX model for GroundFOX from DCP Rosetta.
#
# Find a combination of 4 different numbers between 1 and 100, such that the sum of the
# squares of the two first numbers is equal to the sum of the squares of the other two
# numbers, i.e. a^2 + b^2 = c^2 + d^2 for a, b, c and d between 1 and 100, all different.
#
# Print the numbers (a, b, c, d).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py session5_hardy_1729_square.json --check

# session5_hardy_1729_square: a FOX model for GroundFOX from DCP Rosetta.
#
# Find 4 different numbers between 1 and 100 such that a^2 + b^2 = c^2 + d^2.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json
#
# Structure (data only): Val = 1..100; a pair (z, w) is a numbered element p = 100*(z-1) + (w-1)
# (Pid, PZ, PW give its entries); EqP(x, y, p) holds when x^2 + y^2 = z^2 + w^2 for the pair p and
# {x, y} differs from {z, w} (the allowed tuples of the one equation); Eqable(x, y) holds when some
# such p exists.
# Theory: a, b, c, d are distinct values. G(x, y) picks the pair (a, b) and H(p) the pair (c, d);
# a witness p with EqP(x, y, p) must be picked for G, so the two sums agree.

FOX = """
invocabulary { Val/1 Pid/1 PZ/2 PW/2 EqP/3 Eqable/2 }
outvocabulary { a/1 b/1 c/1 d/1 Gx/1 G/2 H/1 }
theory {
    ? v [Val(v)] : a(v).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~a(v) | ~a(w).
    ? v [Val(v)] : b(v).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~b(v) | ~b(w).
    ? v [Val(v)] : c(v).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~c(v) | ~c(w).
    ? v [Val(v)] : d(v).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~d(v) | ~d(w).

    ! v [Val(v)] : ~a(v) | ~b(v).
    ! v [Val(v)] : ~a(v) | ~c(v).
    ! v [Val(v)] : ~a(v) | ~d(v).
    ! v [Val(v)] : ~b(v) | ~c(v).
    ! v [Val(v)] : ~b(v) | ~d(v).
    ! v [Val(v)] : ~c(v) | ~d(v).

    ? x [Val(x)] : Gx(x).
    ! x [Val(x)] : ? y [Val(y)] : G(x, y) | ~Gx(x).
    ! x [Val(x)] : ! y [Val(y) & ~Eqable(x, y)] : ~G(x, y).
    ! x [Val(x)] : ! y [Val(y)] : ~G(x, y) | a(x).
    ! x [Val(x)] : ! y [Val(y)] : ~G(x, y) | b(y).
    ! x [Val(x)] : ! y [Eqable(x, y)] : ? p [EqP(x, y, p)] : H(p) | ~G(x, y).
    ! p [Pid(p)] : ! z [PZ(p, z)] : ~H(p) | c(z).
    ! p [Pid(p)] : ! w [PW(p, w)] : ~H(p) | d(w).
}
"""


def structure(instance):
    n = 100
    pairs = [(z, w) for z in range(1, n + 1) for w in range(1, n + 1)]
    by_sum = {}
    for z, w in pairs:
        by_sum.setdefault(z * z + w * w, []).append((z, w))
    eqp = []
    eqable = set()
    for z, w in pairs:
        p = (z - 1) * n + (w - 1)
        for x, y in by_sum[z * z + w * w]:
            if {x, y} != {z, w}:
                eqp.append((x, y, p))
                eqable.add((x, y))
    return {
        "Val": range(1, n + 1),
        "Pid": range(n * n),
        "PZ": [((z - 1) * n + (w - 1), z) for z, w in pairs],
        "PW": [((z - 1) * n + (w - 1), w) for z, w in pairs],
        "EqP": eqp,
        "Eqable": sorted(eqable),
    }
