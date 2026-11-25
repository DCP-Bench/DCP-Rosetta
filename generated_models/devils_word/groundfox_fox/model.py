# devils_word: a FOX model for GroundFOX from DCP Rosetta.
#
# Given an array of integers, insert '+' or '-' operators before each integer in the array so
# that summing them up will result in a given total (666 for the devil's word).
#
# Print the array with the correct signs (result). For example, if the given array is [1, 2,
# 3], and the total is 4, then the result array should be [-1, 2, 3].
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py devils_word.json --check

# devils_word: a FOX model for GroundFOX from DCP Rosetta.
#
# Insert '+' or '-' before each integer of arr so that the signed sum equals total.
# result[i] is the signed value: arr[i] for '+', -arr[i] for '-'.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Ix/1 Nx/2 Win/2 Plus/3 Keep/2 PBan/2 KBan/2 Pv/2 Nv/2 Vals/2 Zr/1 Tg/1 Lst/1 }
outvocabulary { result/2 sg/2 P/2 }
theory {
    ! i [Ix(i)] : sg(i, 1) | sg(i, 0).
    ! i [Ix(i)] : ~sg(i, 1) | ~sg(i, 0).
    ! i [Ix(i)] : ? v [Vals(i, v)] : result(i, v).
    ! i [Ix(i)] : ! v [Vals(i, v)] : ! w [Vals(i, w) & v ~= w] : ~result(i, v) | ~result(i, w).
    ! i [Ix(i)] : ! v [Pv(i, v)] : ~sg(i, 1) | result(i, v).
    ! i [Ix(i)] : ! v [Pv(i, v)] : ~result(i, v) | sg(i, 1).
    ! i [Ix(i)] : ! v [Nv(i, v)] : sg(i, 1) | result(i, v).
    ! i [Ix(i)] : ! v [Nv(i, v)] : ~result(i, v) | ~sg(i, 1).
    ! z [Zr(z)] : P(0, z).
    ! l [Lst(l)] : ? s [Tg(s)] : P(l, s).
    ! i [Ix(i)] : ! j [Nx(i, j)] : ! s [Win(i, s)] : ! t [Plus(i, s, t)] : ~P(i, s) | ~sg(i, 1) | P(j, t).
    ! i [Ix(i)] : ! j [Nx(i, j)] : ! s [Keep(i, s)] : ~P(i, s) | sg(i, 1) | P(j, s).
    ! i [Ix(i)] : ! s [PBan(i, s)] : ~P(i, s) | ~sg(i, 1).
    ! i [Ix(i)] : ! s [KBan(i, s)] : ~P(i, s) | sg(i, 1).
}
"""


def _elem(x):
    # FOX numbers have no sign: -k is the element "negk".
    return x if x >= 0 else "neg%d" % (-x)


def structure(instance):
    arr = [int(a) for a in instance["arr"]]
    total = int(instance["total"])
    n = len(arr)
    grand = sum(arr)
    # Signed sum = 2 * (sum of '+' items) - grand, so the '+' items must sum to target.
    target = (total + grand) // 2 if (total + grand) % 2 == 0 else None
    # States are the '+' partial sums shifted to be non-negative.
    shift = -sum(a for a in arr if a < 0)

    # Subset sums of the prefix arr[:i] and of the suffix arr[i:] (data only).
    pre = [{0}]
    for a in arr:
        prev = pre[-1]
        pre.append(prev | {p + a for p in prev})
    suf = [None] * (n + 1)
    suf[n] = {0}
    for i in range(n - 1, -1, -1):
        nxt = suf[i + 1]
        suf[i] = nxt | {p + arr[i] for p in nxt}
    # R[i]: partial '+' sums after i items that the remaining items can complete to target.
    R = []
    for i in range(n + 1):
        if target is None:
            R.append(set())
        else:
            R.append({p for p in pre[i] if target - p in suf[i]})

    win, plus, keep, pban, kban = [], [], [], [], []
    for i in range(n + 1):
        for p in sorted(R[i]):
            win.append((i, p + shift))
    for i, a in enumerate(arr):
        for p in sorted(R[i]):
            s = p + shift
            if p + a in R[i + 1]:
                plus.append((i, s, p + a + shift))
            else:
                pban.append((i, s))
            if p in R[i + 1]:
                keep.append((i, s))
            else:
                kban.append((i, s))

    pv = [(i, _elem(a)) for i, a in enumerate(arr)]
    nv = [(i, _elem(-a)) for i, a in enumerate(arr) if a != 0]
    vals = pv + nv
    tg = [target + shift] if target is not None and target in R[n] else []

    top = max([n, 1, shift + sum(a for a in arr if a > 0)]
              + ([target + shift] if target is not None else []))
    negs = sorted({abs(a) for a in arr if a != 0})
    domain = list(range(top + 1)) + ["neg%d" % k for k in negs]

    return {
        "domain": domain,
        "Ix": list(range(n)),
        "Nx": [(i, i + 1) for i in range(n)],
        "Win": win,
        "Plus": plus,
        "Keep": keep,
        "PBan": pban,
        "KBan": kban,
        "Pv": pv,
        "Nv": nv,
        "Vals": vals,
        "Zr": [shift],
        "Tg": tg,
        "Lst": [n],
    }
