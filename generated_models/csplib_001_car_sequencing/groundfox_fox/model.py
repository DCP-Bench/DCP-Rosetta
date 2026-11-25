# csplib_001_car_sequencing: a FOX model for GroundFOX from DCP Rosetta.
#
# A number of cars are to be produced; they are not identical, because different options are
# available as variants on the basic model. The assembly line has different stations which
# install the various options (air-conditioning, sunroof, etc.). These stations have been
# designed to handle at most a certain percentage of the cars passing along the assembly line.
# Furthermore, the cars requiring a certain option must not be bunched together, otherwise the
# station will not be able to cope. Consequently, the cars must be arranged in a sequence so
# that the capacity of each station is never exceeded. For instance, if a particular station
# can only cope with at most half of the cars passing along the line, the sequence must be
# built so that at most 1 car in any 2 requires that option.
#
# Print the sequence of car types in the assembly line (sequence); each car type is
# represented by a number starting from 0.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_001_car_sequencing.json --check

# csplib_001_car_sequencing: a FOX model for GroundFOX from DCP Rosetta.

FOX = """
invocabulary { Pos/1 Slot/1 Last/1 Nxt/2 Typ/1 Option/1 Req/2 NReq/2 Dem/2 TCnt/2 TSucc/3 Wcnt/1 Wsucc/2 WStart/2 InW/3 WEnd/3 Over/2 }
outvocabulary { sequence/2 hasopt/2 tal/3 wc/4 }
theory {
    ! p [Pos(p)] : ? c [Typ(c)] : sequence(p, c).
    ! p [Pos(p)] : ! c [Typ(c)] : ! d [Typ(d) & c ~= d] : ~sequence(p, c) | ~sequence(p, d).
    ! p [Pos(p)] : ! k [Option(k)] : ! c [Typ(c) & Req(c, k)] : ~sequence(p, c) | hasopt(p, k).
    ! p [Pos(p)] : ! k [Option(k)] : ! c [Typ(c) & NReq(c, k)] : ~sequence(p, c) | ~hasopt(p, k).
    ! c [Typ(c)] : tal(c, 0, 0).
    ! c [Typ(c)] : ! l [Slot(l)] : ? t [TCnt(c, t)] : tal(c, l, t).
    ! c [Typ(c)] : ! p [Pos(p)] : ! q [Nxt(p, q)] : ! d [Dem(c, d)] : ~tal(c, p, d) | ~sequence(p, c).
    ! c [Typ(c)] : ! p [Pos(p)] : ! q [Nxt(p, q)] : ! t [TCnt(c, t)] : ! u [TSucc(c, t, u)] : ~tal(c, p, t) | ~sequence(p, c) | tal(c, q, u).
    ! c [Typ(c)] : ! p [Pos(p)] : ! q [Nxt(p, q)] : ! t [TCnt(c, t)] : ~tal(c, p, t) | sequence(p, c) | tal(c, q, t).
    ! c [Typ(c)] : ! p [Pos(p)] : ! q [Nxt(p, q)] : ! t [TCnt(c, t)] : ~tal(c, q, t) | sequence(p, c) | tal(c, p, t).
    ! c [Typ(c)] : ! p [Pos(p)] : ! q [Nxt(p, q)] : ! t [TCnt(c, t)] : ! u [TSucc(c, t, u)] : ~tal(c, q, u) | ~sequence(p, c) | tal(c, p, t).
    ! c [Typ(c)] : ! p [Pos(p)] : ! q [Nxt(p, q)] : ~tal(c, q, 0) | ~sequence(p, c).
    ! c [Typ(c)] : ! l [Last(l)] : ! t [TCnt(c, t) & ~Dem(c, t)] : ~tal(c, l, t).
    ! c [Typ(c)] : ! l [Last(l)] : ! d [Dem(c, d)] : tal(c, l, d).
    ! k [Option(k)] : ! s [WStart(k, s)] : wc(k, s, s, 0).
    ! k [Option(k)] : ! s [WStart(k, s)] : ! p [InW(k, s, p)] : ? t [Wcnt(t)] : wc(k, s, p, t).
    ! k [Option(k)] : ! s [WStart(k, s)] : ! e [WEnd(k, s, e)] : ? t [Wcnt(t)] : wc(k, s, e, t).
    ! k [Option(k)] : ! s [WStart(k, s)] : ! p [InW(k, s, p)] : ! q [Nxt(p, q)] : ! t [Wcnt(t)] : ! u [Wsucc(t, u)] : ~wc(k, s, p, t) | ~hasopt(p, k) | wc(k, s, q, u).
    ! k [Option(k)] : ! s [WStart(k, s)] : ! p [InW(k, s, p)] : ! q [Nxt(p, q)] : ! t [Wcnt(t)] : ~wc(k, s, p, t) | hasopt(p, k) | wc(k, s, q, t).
    ! k [Option(k)] : ! s [WStart(k, s)] : ! p [InW(k, s, p)] : ! q [Nxt(p, q)] : ! t [Wcnt(t)] : ~wc(k, s, q, t) | hasopt(p, k) | wc(k, s, p, t).
    ! k [Option(k)] : ! s [WStart(k, s)] : ! p [InW(k, s, p)] : ! q [Nxt(p, q)] : ! t [Wcnt(t)] : ! u [Wsucc(t, u)] : ~wc(k, s, q, u) | ~hasopt(p, k) | wc(k, s, p, t).
    ! k [Option(k)] : ! s [WStart(k, s)] : ! p [InW(k, s, p)] : ! q [Nxt(p, q)] : ~wc(k, s, q, 0) | ~hasopt(p, k).
    ! k [Option(k)] : ! s [WStart(k, s)] : ! p [InW(k, s, p)] : ! t [Over(k, t)] : ~wc(k, s, p, t).
    ! k [Option(k)] : ! s [WStart(k, s)] : ! e [WEnd(k, s, e)] : ! t [Over(k, t)] : ~wc(k, s, e, t).
}
"""


def structure(instance):
    demand = instance["demand"]
    at_most = instance["at_most"]
    per = instance["per_slots"]
    req = instance["requires"]
    C, K = len(demand), len(at_most)
    L = sum(demand)
    Q = max(per)
    return {
        "Pos": range(L),
        "Slot": range(L + 1),
        "Last": [L],
        "Nxt": [(p, p + 1) for p in range(L)],
        "Typ": range(C),
        "Option": range(K),
        "Req": [(c, k) for c in range(C) for k in range(K) if req[c][k]],
        "NReq": [(c, k) for c in range(C) for k in range(K) if not req[c][k]],
        "Dem": [(c, demand[c]) for c in range(C)],
        # Counts of one type over the sequence, bounded by its demand.
        "TCnt": [(c, t) for c in range(C) for t in range(demand[c] + 1)],
        "TSucc": [(c, t, t + 1) for c in range(C) for t in range(demand[c])],
        # Counts of an option inside one window: never exceed the largest window.
        "Wcnt": range(Q + 1),
        "Wsucc": [(t, t + 1) for t in range(Q)],
        "WStart": [(k, s) for k in range(K) for s in range(L - per[k] + 1)],
        "InW": [(k, s, p) for k in range(K) for s in range(L - per[k] + 1)
                for p in range(s, s + per[k])],
        "WEnd": [(k, s, s + per[k]) for k in range(K) for s in range(L - per[k] + 1)],
        "Over": [(k, t) for k in range(K) for t in range(Q + 1) if t > at_most[k]],
    }
