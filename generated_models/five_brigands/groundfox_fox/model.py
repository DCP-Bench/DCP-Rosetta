# five_brigands: a FOX model for GroundFOX from DCP Rosetta.
#
# The five Spanish brigands, Alfonso, Benito, Carlos, Diego, and Esteban, were counting their
# spoils after a raid, when it was found that they had captured altogether exactly 200
# doubloons. One of the band pointed out that if Alfonso had twelve times as much, Benito
# three times as much, Carlos the same amount, Diego half as much, and Esteban one- third as
# much, they would still have altogether just 200 doubloons. How many doubloons had each?
# Also, no brigand had less than one doubloon.
#
# Print the number of doubloons that each brigand may have according to the above information
# (A, B, C, D, E).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py five_brigands.json --check

# five_brigands: a FOX model for GroundFOX from DCP Rosetta.
#
# Five brigands A, B, C, D, E each hold a positive integer number of doubloons, with
#   A + B + C + D + E = 200                      (equation 1)
#   12A + 3B + C + D/2 + E/3 = 200               (equation 2)
# Equation 2 scaled by 6 is 72A + 18B + 6C + 3D + 2E = 1200, an integer equation.
#
# Encoding: each equation is one running-sum chain over the stages A, B, C, D, E.
#   chain P has coefficients (1, 1, 1, 1, 1) and target 200;
#   chain Q has coefficients (72, 18, 6, 3, 2) and target 1200.
# Data per chain (computed from that chain's own equation alone): the totals reachable
# after each stage, using values 1..196 (from the sum equation alone), cut at the target.
# Every layer has exactly one true state; forced transitions Inc(s, v, t) carry a state
# to its successor, and overflow or dead transitions are banned by Ban(s, v). The last
# layer is the target, so the chain is satisfied only when its total equals the target.
# No combined bound or propagated domain is precomputed: the two chains interact only
# through the shared brigand values in the theory.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

NAMES = ["A", "B", "C", "D", "E"]
VAL = list(range(1, 197))          # from the sum equation: each value in 1..196
TOP = 1200                         # largest running total in either chain
CHAINS = {                         # name: (coefficient per brigand in NAMES order, target)
    "P": ([1, 1, 1, 1, 1], 200),
    "Q": ([72, 18, 6, 3, 2], 1200),
}


def _layers(coefs, target):
    """Running totals reachable under one chain's own equation, cut at its target."""
    layers = [[0]]
    for c in coefs:
        layers.append(sorted({s + c * v for s in layers[-1] for v in VAL if s + c * v <= target}))
    layers[-1] = [target]
    return layers


def _consecutive(xs):
    return [(a, b) for a, b in zip(xs, xs[1:])]


def _ladder(lines, atom, aux, guard, nxt):
    """At most one true atom over guard: aux(x) means some atom is true at or before x."""
    lines.append("    ! x [%s(x)] : ~%s(x) | %s(x)." % (guard, atom, aux))
    lines.append("    ! x : ! y [%s(x, y)] : ~%s(x) | %s(y)." % (nxt, aux, aux))
    lines.append("    ! x : ! y [%s(x, y)] : ~%s(x) | ~%s(y)." % (nxt, aux, atom))


def _build():
    arity = {"Num": 1, "Zero": 1}
    data = {"Num": list(range(TOP + 1)), "Zero": [0]}
    outs = {}
    lines = []

    # each brigand holds exactly one value from its domain
    for x in NAMES:
        arity["Val" + x] = 1
        arity["Succ" + x] = 2
        data["Val" + x] = VAL
        data["Succ" + x] = _consecutive(VAL)
        outs[x] = 1
        outs["Q" + x] = 1
        lines.append("    ? v [Val%s(v)] : %s(v)." % (x, x))
        lines.append("    ! v [Num(v) & ~Val%s(v)] : ~%s(v)." % (x, x))
        _ladder(lines, x, "Q" + x, "Val" + x, "Succ" + x)

    # one running-sum chain per equation: exactly one state per layer, forced transitions,
    # banned overflow and dead transitions, final layer = the target
    for ch, (coefs, target) in CHAINS.items():
        layers = _layers(coefs, target)
        m = len(coefs)
        lines.append("    ! z [Zero(z)] : S%s0(z)." % ch)
        for k in range(m + 1):
            R, U = "Reach%s%d" % (ch, k), "Next%s%d" % (ch, k)
            S, P = "S%s%d" % (ch, k), "P%s%d" % (ch, k)
            arity[R], arity[U] = 1, 2
            data[R], data[U] = layers[k], _consecutive(layers[k])
            outs[S], outs[P] = 1, 1
            lines.append("    ! s [Num(s) & ~%s(s)] : ~%s(s)." % (R, S))
            lines.append("    ? s [%s(s)] : %s(s)." % (R, S))
            _ladder(lines, S, P, R, U)
            if k == m:
                lines.append("    ! s [%s(s)] : %s(s)." % (R, S))  # the chain ends at its target
                continue
            X = NAMES[k]
            I, Bn = "Inc%s%d" % (ch, k), "Ban%s%d" % (ch, k)
            arity[I], arity[Bn] = 3, 2
            inc, ban = [], []
            nxt = set(layers[k + 1])
            for s in layers[k]:
                for v in VAL:
                    t = s + coefs[k] * v
                    if t in nxt:
                        inc.append((s, v, t))
                    else:
                        ban.append((s, v))
            data[I], data[Bn] = inc, ban
            lines.append("    ! s [%s(s)] : ! v [Val%s(v)] : ! t [%s(s, v, t)] : "
                         "~%s(s) | ~%s(v) | S%s%d(t)." % (R, X, I, S, X, ch, k + 1))
            lines.append("    ! s : ! v [%s(s, v)] : ~%s(s) | ~%s(v)." % (Bn, S, X))

    inv = " ".join("%s/%d" % (k, arity[k]) for k in sorted(arity))
    outv = " ".join("%s/%d" % (k, outs[k]) for k in sorted(outs))
    fox = ("invocabulary { " + inv + " }\n"
           "outvocabulary { " + outv + " }\n"
           "theory {\n" + "\n".join(lines) + "\n}\n")
    return fox, data


FOX, _DATA = _build()


def structure(instance):
    return dict(_DATA)
