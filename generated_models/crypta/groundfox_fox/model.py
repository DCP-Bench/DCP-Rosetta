# crypta: a FOX model for GroundFOX from DCP Rosetta.
#
# Cryptarithmetic puzzle, solve the operation:
#
# ```text B A I J J A J I I A H F C F E B B J E A + D H F G A B C D I D B I F F A G F E J E
# ----------------------------------------- = G J E G A C D D H F A F J B F I H E E F ```
#
# where all letters are distinct digits from 0 to 9, and the first letter of each number
# cannot be zero.
#
# Print the digit of each letter (A, B, C, D, E, F, G, H, I, J).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py crypta.json --check

# crypta: a FOX model for GroundFOX from DCP Rosetta.
#
# Cryptarithm: BAIJJAJIIAHFCFEBBJEA + DHFGABCDIDBIFFAGFEJE = GJEGACDDHFAFJBFIHEEF,
# all letters distinct digits; the first letter of each number is nonzero.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

ADDENDS = ['BAIJJAJIIAHFCFEBBJEA', 'DHFGABCDIDBIFFAGFEJE']
RESULT = "GJEGACDDHFAFJBFIHEEF"
LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
LEADING = ['B', 'D', 'G']


def _columns():
    p = len(RESULT)
    cols = {q: [] for q in range(1, p + 1)}
    for w in ADDENDS:
        assert len(w) <= p
        for k, ch in enumerate(reversed(w)):
            cols[k + 1].append(ch)
    res = {k + 1: ch for k, ch in enumerate(reversed(RESULT))}
    cin = 0
    smax = 0
    cmax = 0
    for q in range(1, p + 1):
        sq = 9 * len(cols[q]) + cin
        smax = max(smax, sq)
        cin = sq // 10
        cmax = max(cmax, cin)
    return p, cols, res, smax, cmax


P, COLS, RES, SMAX, CMAX = _columns()
RMAX = max(len(v) for v in COLS.values())


def _theory():
    lines = []
    for L in LETTERS:
        lines.append(f"? v [Dig(v)] : {L}(v).")
        lines.append(f"! v [Dig(v)] : ! w [Dig(w) & ~(v = w)] : ~{L}(v) | ~{L}(w).")
    for i, a in enumerate(LETTERS):
        for b in LETTERS[i + 1:]:
            lines.append(f"! v [Dig(v)] : ~{a}(v) | ~{b}(v).")
    for L in LEADING:
        lines.append(f"! u [u = 0] : ~{L}(0).")
    # carry into column 1 is 0; carry out of the top column is 0
    lines.append("! z [Zr(z)] : Cy(0, z).")
    lines.append("! z [Zr(z)] : ! c [Cr(c) & ~Zr(c)] : ~Cy(0, c).")
    lines.append(f"! z [Zr(z)] : Cy({P}, z).")
    for q in range(1, P + 1):
        occ = COLS[q]
        R = len(occ)

        def ref(r, x):
            return f"Cy({q - 1}, {x})" if r == 0 else f"Ps({q}, {r}, {x})"

        for r, X in enumerate(occ):
            lines.append(f"! s [Sts(s)] : ! v [Dig(v)] : ! t [Adds(s, v, t)] : ~{ref(r, 's')} | ~{X}(v) | {ref(r + 1, 't')}.")
        d = RES[q]
        lines.append(f"! t [Sts(t)] : ! d [Dig(d)] : ! c [Cr(c) & ~Fin(t, d, c)] : ~{ref(R, 't')} | ~{d}(d) | ~Cy({q}, c).")
        lines.append(f"? c [Cr(c)] : Cy({q}, c).")
        lines.append(f"! c [Cr(c)] : ! c2 [Cr(c2) & ~(c = c2)] : ~Cy({q}, c) | ~Cy({q}, c2).")
    return "\n".join(lines)



FOX = (
    "invocabulary { Dig/1 Sts/1 Cr/1 Zr/1 Adds/3 Fin/3 }\n"
    "outvocabulary { " + " ".join(f"{L}/1" for L in LETTERS) + " Ps/3 Cy/2 }\n"
    "theory {\n" + _theory() + "\n}\n"
)


def structure(instance):
    top = max(SMAX, RMAX, P)
    return {
        "domain": range(top + 1),
        "Dig": range(10),
        "Sts": range(SMAX + 1),
        "Cr": range(CMAX + 1),
        "Zr": [0],
        "Adds": [(s, v, s + v) for s in range(SMAX + 1) for v in range(10) if s + v <= SMAX],
        "Fin": [(d + 10 * c, d, c) for c in range(CMAX + 1) for d in range(10) if d + 10 * c <= SMAX],
    }
