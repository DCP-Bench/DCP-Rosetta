# broken_weights: a FOX model for GroundFOX from DCP Rosetta.
#
# A merchant had a measuring weight that broke into a number of pieces as the result of a
# fall. When the pieces were subsequently weighed, it was found that the weight of each piece
# was a whole number of pounds and that the pieces could be used to weigh every integral
# weight between 1 and the total weight. What were the weights of the pieces?
#
# Note that since this was a 17th-century merchant, he of course used a balance scale to weigh
# things. So, for example, he could use a 1-pound weight and a 4-pound weight to weigh a
# 3-pound object, by placing the 3-pound object and 1-pound weight on one side of the scale,
# and the 4-pound weight on the other side.
#
# Print the weights of the pieces (weights) as a list of integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py broken_weights.json --check

"""broken_weights: a FOX model for GroundFOX from DCP Rosetta.

weights(i, v): piece i (0 .. n-1) weighs v in 1..m, and the pieces sum to m (the total
weight). Tot is a deterministic chain over the pieces: it forces the total to be m.
R(l, r): sum r - m is reachable as a signed sum (-1, 0 or +1 per piece) of the first l pieces,
with offset m. R is exact: R(l+1, r) holds only with a witness Ap(l, r, mv) for a move mv
(piece l on the left or on the right, value v = mv or mv - m) from a source state that R
reaches. Every target t in 1..m must be reachable after all n pieces.
"""

FOX = """
invocabulary { Piece/1 Nx/2 Zero/1 Last/1 Sm/1 Val/1 Start/1 Fin/1 Mv/1 MvV/2 Src/3 Dst/3 NoSrc/2
               TSm/1 TAdd/3 TSNe/1 }
outvocabulary { weights/2 Tot/2 R/2 Ap/3 }
theory {
    ! i [Piece(i)] : ? v [Val(v)] : weights(i, v).
    ! i [Piece(i)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~weights(i, v) | ~weights(i, w).

    ! u [u = 0] : Tot(0, 0).
    ! i [Piece(i)] : ! j [Nx(i, j)] : ! s [TSm(s)] : ! v [Val(v)] : ! r [TAdd(s, v, r)] : ~Tot(i, s) | ~weights(i, v) | Tot(j, r).
    ! l [Last(l)] : ! s [TSNe(s)] : ~Tot(l, s).

    ! l [Zero(l)] : ! u [Start(u)] : R(l, u).
    ! l [Zero(l)] : ! r [Sm(r) & ~Start(r)] : ~R(l, r).
    ! l : ! lp [Nx(l, lp)] : ! r [Sm(r)] : ~R(l, r) | R(lp, r).
    ! l : ! lp [Nx(l, lp)] : ! r [Sm(r)] : ? mv [Mv(mv)] : Ap(l, r, mv) | R(l, r) | ~R(lp, r).
    ! l [Piece(l)] : ! r [Sm(r)] : ! mv [Mv(mv)] : ! s [Src(r, mv, s)] : ~Ap(l, r, mv) | R(l, s).
    ! l [Piece(l)] : ! r [Sm(r)] : ! mv [Mv(mv)] : ! v [MvV(mv, v)] : ~Ap(l, r, mv) | weights(l, v).
    ! l [Piece(l)] : ! r [Sm(r)] : ! mv [NoSrc(r, mv)] : ~Ap(l, r, mv).
    ! l [Piece(l)] : ! s [Sm(s)] : ! mv [Mv(mv)] : ! v [MvV(mv, v)] : ! r [Dst(s, mv, r)] : ~R(l, s) | ~weights(l, v) | Ap(l, r, mv).
    ! l [Last(l)] : ! r [Fin(r)] : R(l, r).
}
"""


def structure(instance):
    n = instance["n"]
    m = instance["m"]
    top = 2 * m
    dst = []
    for s in range(top + 1):
        for mv in range(1, top + 1):
            v = mv if mv <= m else mv - m
            r = s + v if mv <= m else s - v
            if 0 <= r <= top:
                dst.append((s, mv, r))
    src = [(r, mv, s) for (s, mv, r) in dst]
    has_src = {(r, mv) for (r, mv, _) in src}
    nosrc = [(r, mv) for r in range(top + 1) for mv in range(1, top + 1) if (r, mv) not in has_src]
    return {
        "Piece": range(n),
        "Nx": [(l, l + 1) for l in range(n)],
        "Zero": [0],
        "Last": [n],
        "Sm": range(top + 1),
        "Val": range(1, m + 1),
        "Start": [m],
        "Fin": range(m + 1, top + 1),
        "Mv": range(1, top + 1),
        "MvV": [(mv, mv if mv <= m else mv - m) for mv in range(1, top + 1)],
        "Src": src,
        "Dst": dst,
        "NoSrc": nosrc,
        "TSm": range(n * m + 1),
        "TAdd": [(s, v, s + v) for s in range(n * m + 1) for v in range(1, m + 1) if s + v <= n * m],
        "TSNe": [s for s in range(n * m + 1) if s != m],
    }
