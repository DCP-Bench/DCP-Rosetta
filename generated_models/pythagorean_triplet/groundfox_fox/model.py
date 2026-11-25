# pythagorean_triplet: a FOX model for GroundFOX from DCP Rosetta.
#
# A Pythagorean triplet is a set of three natural numbers a, b and c for which a^2 + b^2 =
# c^2. The order of a and b does not matter.
#
# For example, 3^2 + 4^2 = 9 + 16 = 25 = 5^2.
#
# There exists exactly one Pythagorean triplet for which a + b + c = 1000.
#
# Print a, b, and c (a, b, c) for this Pythagorean triplet such that a + b + c = 1000.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py pythagorean_triplet.json --check

# pythagorean_triplet: a FOX model for GroundFOX from DCP Rosetta.
#
# A Pythagorean triplet is a set of three natural numbers a, b and c for which
# a^2 + b^2 = c^2. The order of a and b does not matter. Find a, b, c with a + b + c = 1000.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Row/1 Ra/2 Rb/2 Rc/2 Rs/2 Tgt/1 Dom/1 }
outvocabulary { a/1 b/1 c/1 Sel/1 }
theory {
    ? i [Row(i)] : Sel(i).
    ! i : ! s [Rs(i, s) & ~Tgt(s)] : ~Sel(i).
    ! i : ! v [Ra(i, v)] : ~Sel(i) | a(v).
    ! i : ! v [Rb(i, v)] : ~Sel(i) | b(v).
    ! i : ! v [Rc(i, v)] : ~Sel(i) | c(v).
    ? v [Dom(v)] : a(v).
    ! v : ! w [Dom(w) & ~(v = w)] : ~a(v) | ~a(w).
    ? v [Dom(v)] : b(v).
    ! v : ! w [Dom(w) & ~(v = w)] : ~b(v) | ~b(w).
    ? v [Dom(v)] : c(v).
    ! v : ! w [Dom(w) & ~(v = w)] : ~c(v) | ~c(w).
    ! v [Dom(v) & ~? j : Ra(j, v)] : ~a(v).
    ! v [Dom(v) & ~? j : Rb(j, v)] : ~b(v).
    ! v [Dom(v) & ~? j : Rc(j, v)] : ~c(v).
    ! v [Dom(v) & ? j : Ra(j, v)] : ? i [Ra(i, v)] : Sel(i) | ~a(v).
    ! v [Dom(v) & ? j : Rb(j, v)] : ? i [Rb(i, v)] : Sel(i) | ~b(v).
    ! v [Dom(v) & ? j : Rc(j, v)] : ? i [Rc(i, v)] : Sel(i) | ~c(v).
}
"""

LIMIT = 1000


def structure(instance):
    rows = []
    for x in range(1, LIMIT + 1):
        for y in range(1, LIMIT + 1):
            z2 = x * x + y * y
            z = int(round(z2 ** 0.5))
            if z <= LIMIT and z * z == z2:
                rows.append((x, y, z))
    n = len(rows)
    # Values that occur in some triple: the only values a, b or c can take.
    vals = sorted({v for r in rows for v in r})
    return {
        "domain": range(max(LIMIT, n) + 1),
        "Dom": vals,
        "Tgt": [LIMIT],
        "Row": range(n),
        "Ra": [(i, r[0]) for i, r in enumerate(rows)],
        "Rb": [(i, r[1]) for i, r in enumerate(rows)],
        "Rc": [(i, r[2]) for i, r in enumerate(rows)],
        "Rs": [(i, r[0] + r[1] + r[2]) for i, r in enumerate(rows)],
    }
