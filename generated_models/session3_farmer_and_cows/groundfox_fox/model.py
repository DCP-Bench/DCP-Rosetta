# session3_farmer_and_cows: a FOX model for GroundFOX from DCP Rosetta.
#
# A farmer has a number of cows, with each cow numbered from 1 up to the total number of cows.
# Each cow gives a quantity of milk equal to its number. The farmer has a number of sons and
# wants to distribute his cows to them according to a given distribution. The total quantity
# of milk produced should be the same for each son. How can he distribute the cows?
#
# Print the assignment of cows to sons (cow_assignments), as a list of integers, where the
# index of the list corresponds to the cow and the value to the son, e.g., [0, 1, 0, 2] means
# that cow 1 goes to son 0, cow 2 to son 1, cow 3 to son 0, and cow 4 to son 2.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py session3_farmer_and_cows.json --check

# session3_farmer_and_cows: a FOX model for GroundFOX from DCP Rosetta.
#
# A farmer has n cows, cow c (0-based, c = 0..n-1) gives c+1 litres of milk. He has k
# sons and a distribution cows_per_son[s]. Assign every cow to one son so that son s gets
# exactly cows_per_son[s] cows and every son gets the same total milk (n(n+1)/2 / k).
# Output cow_assignments[c] = son of cow c.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Cow/1 Lay/1 Last/1 Son/1 Share/1 Next/2 WL/2 Take/4 TakeBan/2 Skip/3 SkipBan/2 CS/2 CInc/3 CTop/2 }
outvocabulary { cow_assignments/2 mil/3 cc/3 }
theory {
    ! c [Cow(c)] : ? s [Son(s)] : cow_assignments(c, s).
    ! c [Cow(c)] : ! s [Son(s)] : ! t [Son(t) & s ~= t] : ~cow_assignments(c, s) | ~cow_assignments(c, t).

    ! s [Son(s)] : mil(0, s, 0).
    ! c [Lay(c)] : ! s [Son(s)] : ? m [WL(c, m)] : mil(c, s, m).
    ! c [Cow(c)] : ! d [Next(c, d)] : ! m [WL(c, m)] : ! m2 [Take(c, d, m, m2)] : ! s [Son(s)] : ~mil(c, s, m) | ~cow_assignments(c, s) | mil(d, s, m2).
    ! c [Cow(c)] : ! d [Next(c, d)] : ! m [Skip(c, d, m)] : ! s [Son(s)] : ~mil(c, s, m) | cow_assignments(c, s) | mil(d, s, m).
    ! c [Cow(c)] : ! m [TakeBan(c, m)] : ! s [Son(s)] : ~mil(c, s, m) | ~cow_assignments(c, s).
    ! c [Cow(c)] : ! m [SkipBan(c, m)] : ! s [Son(s)] : ~mil(c, s, m) | cow_assignments(c, s).
    ! c [Last(c)] : ! m [Share(m)] : ! s [Son(s)] : mil(c, s, m).
    ! c [Cow(c)] : ! d [Next(c, d)] : ! m2 [WL(d, m2)] : ! m [Take(c, d, m, m2)] : ! s [Son(s)] : ~mil(d, s, m2) | ~cow_assignments(c, s) | mil(c, s, m).
    ! c [Cow(c)] : ! d [Next(c, d)] : ! m2 [Skip(c, d, m2)] : ! s [Son(s)] : ~mil(d, s, m2) | cow_assignments(c, s) | mil(c, s, m2).

    ! s [Son(s)] : cc(0, s, 0).
    ! c [Lay(c)] : ! s [Son(s)] : ? j [CS(s, j)] : cc(c, s, j).
    ! c [Cow(c)] : ! d [Next(c, d)] : ! s [Son(s)] : ! j2 [CS(s, j2)] : ! j [CInc(s, j, j2)] : ~cc(d, s, j2) | ~cow_assignments(c, s) | cc(c, s, j).
    ! c [Cow(c)] : ! d [Next(c, d)] : ! s [Son(s)] : ! j2 [CS(s, j2)] : ~cc(d, s, j2) | cow_assignments(c, s) | cc(c, s, j2).
    ! c [Cow(c)] : ! d [Next(c, d)] : ! s [Son(s)] : ! j [CS(s, j)] : ! j2 [CInc(s, j, j2)] : ~cc(c, s, j) | ~cow_assignments(c, s) | cc(d, s, j2).
    ! c [Cow(c)] : ! d [Next(c, d)] : ! s [Son(s)] : ! j [CS(s, j)] : ~cc(c, s, j) | cow_assignments(c, s) | cc(d, s, j).
    ! c [Cow(c)] : ! s [Son(s)] : ! j [CTop(s, j)] : ~cc(c, s, j) | ~cow_assignments(c, s).
    ! c [Last(c)] : ! s [Son(s)] : ! j [CTop(s, j)] : cc(c, s, j).
}
"""

FLAGS = []


def _windows(n, total_share):
    """Milk window per layer i (cows 0..i-1 decided): values m that are reachable from 0
    with cows 0..i-1 (all of 0..i(i+1)/2) and from which total_share is still reachable
    with cows i..n-1 (milk i+1..n). Computed for the milk constraint alone."""
    T = total_share
    suffix = [0] * (n + 1)          # bitmask of subset sums of milk {i+1..n}
    suffix[n] = 1
    for i in range(n - 1, -1, -1):
        suffix[i] = suffix[i + 1] | (suffix[i + 1] << (i + 1))
    windows = []
    for i in range(n + 1):
        reach = min(T, i * (i + 1) // 2) if T >= 0 else -1
        w = set()
        for m in range(0, reach + 1):
            if (T - m) >= 0 and (suffix[i] >> (T - m)) & 1:
                w.add(m)
        windows.append(w)
    return windows


def structure(instance):
    n = instance["num_cows"]
    k = instance["num_sons"]
    cps = instance["cows_per_son"]
    total = n * (n + 1) // 2
    T = total // k if total % k == 0 else -1
    W = _windows(n, T) if T >= 0 else [set() for _ in range(n + 1)]

    cows = list(range(n))
    layers = list(range(n + 1))
    take, take_ban, skip, skip_ban = [], [], [], []
    for c in range(n):
        for m in sorted(W[c]):
            m2 = m + c + 1
            if m2 in W[c + 1]:
                take.append((c, c + 1, m, m2))
            else:
                take_ban.append((c, m))
            if m in W[c + 1]:
                skip.append((c, c + 1, m))
            else:
                skip_ban.append((c, m))

    cs, cinc, ctop = [], [], []
    for s, cnt in enumerate(cps):
        for j in range(cnt + 1):
            cs.append((s, j))
        for j in range(cnt):
            cinc.append((s, j, j + 1))
        ctop.append((s, cnt))

    wl = [(c, m) for c in layers for m in sorted(W[c])]
    domain = set(range(max(n, k, max(cps) if cps else 0, max(T, 0)) + 1))
    return {
        "domain": sorted(domain),
        "Cow": cows,
        "Lay": layers,
        "Last": [n],
        "Son": list(range(k)),
        "Share": [T] if T >= 0 else [],
        "Next": [(c, c + 1) for c in range(n)],
        "WL": wl,
        "Take": take,
        "TakeBan": take_ban,
        "Skip": skip,
        "SkipBan": skip_ban,
        "CS": cs,
        "CInc": cinc,
        "CTop": ctop,
    }
