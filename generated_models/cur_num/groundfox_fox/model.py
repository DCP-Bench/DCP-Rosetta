# cur_num: a FOX model for GroundFOX from DCP Rosetta.
#
# The number 48 has this peculiarity, that if you add 1 to it the result is a square number,
# and if you add 1 to its half, you also get a square number.
#
# Print another number with this peculiarity (peculiar) between 1 and 10000.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py cur_num.json --check

FOX = """
invocabulary { Val/1 Next/2 Sq/1 Half/1 Known/1 }
outvocabulary { peculiar/1 Pre/1 }
theory {
    ? v [Val(v)] : peculiar(v).
    ! v [Val(v) & ~Sq(v)] : ~peculiar(v).
    ! v [Val(v) & ~Half(v)] : ~peculiar(v).
    ! v [Known(v)] : ~peculiar(v).
    ! v [Val(v)] : ~peculiar(v) | Pre(v).
    ! v : ! w [Next(v, w)] : ~Pre(v) | Pre(w).
    ! v : ! w [Next(v, w)] : ~Pre(v) | ~peculiar(w).
}
"""

FLAGS = []


def _is_square(n):
    r = int(n ** 0.5)
    while r * r > n:
        r -= 1
    while (r + 1) * (r + 1) <= n:
        r += 1
    return r * r == n


def structure(instance):
    top = 10000
    values = list(range(1, top + 1))
    sq = [p for p in values if _is_square(p + 1)]
    half = [p for p in values if p % 2 == 0 and _is_square(p // 2 + 1)]
    return {
        "domain": range(0, top + 1),
        "Val": values,
        "Next": [(v, v + 1) for v in range(1, top)],
        "Sq": sq,
        "Half": half,
        "Known": [48],
    }
