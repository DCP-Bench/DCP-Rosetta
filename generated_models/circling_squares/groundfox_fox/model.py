# circling_squares: a FOX model for GroundFOX from DCP Rosetta.
#
# Circling the squares:
#
# The puzzle is to place a different number in each of the ten squares so that the sum of the
# squares of any two adjacent numbers shall be equal to the sum of the squares of the two
# numbers diametrically opposite to them. The four numbers placed, as examples, must stand as
# they are. The square of 16 is 256, and the square of 2 is 4. Add these together, and the
# result is 260. Also—the square of 14 is 196, and the square of 8 is 64. These together also
# make 260. Now, in precisely the same way, B and C should be equal to G and H (the sum will
# not necessarily be 260), A and K to F and E, H and I to C and D, and so on, with any two
# adjoining squares in the circle.
#
# All you have to do is to fill in the remaining six numbers. Fractions are not allowed, and I
# shall show that no number need contain more than two figures.
#
# Print the 10 numbers in the circle (A, B, C, D, E, F, G, H, I, K) when A=16, B=2, F=8, G=14.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py circling_squares.json --check

# circling_squares: a FOX model for GroundFOX from DCP Rosetta.
#
# Ten positions A, B, C, D, E, F, G, H, I, K sit in a circle (A next to B and K). Each holds
# a different integer 1..99. For every adjacent pair of positions, the sum of the squares of
# the pair equals the sum of the squares of the diametrically opposite pair. A=16, B=2,
# F=8, G=14 are given.
#
# Equations (positions in circle order P0..P9, opposite of Pi is Pi+5):
#   eq1: B^2 + C^2 = G^2 + H^2   -> C^2 - H^2 = 192       (binary, Diff192)
#   eq2: C^2 + D^2 = H^2 + I^2   -> quaternary (Need)
#   eq3: D^2 + E^2 = I^2 + K^2   -> quaternary (Need)
#   eq4: E^2 + F^2 = K^2 + A^2   -> E^2 - K^2 = 192       (binary, Diff192)
#   eq0 (A,B,F,G) is fixed by the givens and needs no clause.
# Every quantity used in the theory is a relation computed in structure().

VAL = range(1, 100)
POSITIONS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]
GIVEN = {"A": 16, "B": 2, "F": 8, "G": 14}


def _theory():
    lines = []
    for p in POSITIONS:
        lines.append(f"? v [Val(v)] : {p}(v).")
        lines.append(f"! v [Val(v)] : ! w [Val(w) & v ~= w] : ~{p}(v) | ~{p}(w).")
    for i, p in enumerate(POSITIONS):
        for q in POSITIONS[i + 1:]:
            lines.append(f"! v [Val(v)] : ~{p}(v) | ~{q}(v).")
    for p, v in GIVEN.items():
        lines.append(f"! u [u = {v}] : {p}({v}).")
    # eq1 and eq4: binary, using Diff192(x, y): x^2 - y^2 = 192. The existential
    # is split by its guard so that every existential sits alone in its body.
    lines.append("! c [Val(c) & ? z : Diff192(c, z)] : ? h [Diff192(c, h)] : H(h) | ~C(c).")
    lines.append("! c [Val(c) & ~? z : Diff192(c, z)] : ~C(c).")
    lines.append("! e [Val(e) & ? z : Diff192(e, z)] : ? k [Diff192(e, k)] : K(k) | ~E(e).")
    lines.append("! e [Val(e) & ~? z : Diff192(e, z)] : ~E(e).")
    # eq2 and eq3: quaternary, using Need(a, b, c, d): a^2 + b^2 = c^2 + d^2.
    # The guards use CandC (values x with x^2 - y^2 = 192 for some y, the only
    # possible C and E) and CandH (the matching y, the only possible H): eq1 and
    # eq4 already force C, E into CandC and H into CandH, so these guards only
    # shrink the quantified ranges. Triples without a witness d are forbidden
    # outright; the others take the existential with the literals in its body.
    lines.append(
        "! a [Val(a) & CandC(a)] : ! b [Val(b)] : ! c [Val(c) & CandH(c) & ? z : Need(a, b, c, z)] : "
        "? d [Need(a, b, c, d)] : I(d) | ~C(a) | ~D(b) | ~H(c)."
    )
    lines.append(
        "! a [Val(a) & CandC(a)] : ! b [Val(b)] : ! c [Val(c) & CandH(c) & ~? z : Need(a, b, c, z)] : "
        "~C(a) | ~D(b) | ~H(c)."
    )
    lines.append(
        "! a [Val(a)] : ! b [Val(b) & CandC(b)] : ! c [Val(c) & ? z : Need(a, b, c, z)] : "
        "? d [Need(a, b, c, d)] : K(d) | ~D(a) | ~E(b) | ~I(c)."
    )
    lines.append(
        "! a [Val(a)] : ! b [Val(b) & CandC(b)] : ! c [Val(c) & ~? z : Need(a, b, c, z)] : "
        "~D(a) | ~E(b) | ~I(c)."
    )
    body = "\n    ".join(lines)
    outs = " ".join(f"{p}/1" for p in POSITIONS)
    return (
        "invocabulary { Val/1 CandC/1 CandH/1 Need/4 Diff192/2 }\n"
        f"outvocabulary {{ {outs} }}\n"
        "theory {\n    " + body + "\n}\n"
    )


FOX = _theory()


def structure(instance):
    vals = list(VAL)
    squares = {v: v * v for v in vals}
    by_sum = {}
    for c in vals:
        for d in vals:
            by_sum.setdefault(squares[c] + squares[d], []).append((c, d))
    need = [
        (a, b, c, d)
        for a in vals
        for b in vals
        for (c, d) in by_sum.get(squares[a] + squares[b], [])
    ]
    diff = [(x, y) for x in vals for y in vals if squares[x] - squares[y] == 192]
    cand_c = sorted({x for x, _ in diff})
    cand_h = sorted({y for _, y in diff})
    return {"domain": VAL, "Val": VAL, "CandC": cand_c, "CandH": cand_h,
            "Need": need, "Diff192": diff}
