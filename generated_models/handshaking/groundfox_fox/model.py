# handshaking: a FOX model for GroundFOX from DCP Rosetta.
#
# Hilary and Jocelyn are married. They invite a number of couples who are friends for dinner.
# When they arrive, they shake hands with each other. Nobody shakes hands with him or herself
# or with his or her spouse. After there has been some handshaking, Jocelyn jumps up on a
# chair and says 'Stop shaking hands!', and then asks how many hands each person has shaken.
# All the answers are different.
#
# Print the number of hands Hilary has shaken (hil).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py handshaking.json --check

# handshaking: a FOX model for GroundFOX from DCP Rosetta.
#
# Hilary (person 0) and Jocelyn (person 1) are married and host num_couples
# invited couples. Nobody shakes hands with self or spouse. Everyone except Jocelyn
# reports a hand count, and all those counts are different. Output hil is Hilary's count.
#
# Encoding: symmetric hand-shake relation H(a, b); for each person an exact
# sequential counter E(a, p, c) over the people p (c = hands among people <= p).
# Couples are interchangeable and the two members of a couple too, so the
# invited husbands are ordered by hand count (and each husband outranks his wife):
# a relabelling of the invited couples, which keeps every solution's hil.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json
FOX = """
invocabulary { Person/1 Asked/1 Spouse/2 Cnt/1 Ge2/1 Prev/2 Start/1 Last/1 Next/2 PairLt/2 Deg/1 Hus/1 NextH/2 Le/2 }
outvocabulary { H/2 E/3 hil/1 }
theory {
    ! a [Person(a)] : ! b [Person(b)] : ~H(a, b) | H(b, a).
    ! a [Person(a)] : ~H(a, a).
    ! a [Person(a)] : ! b [Spouse(a, b)] : ~H(a, b).
    ! a [Person(a)] : ! s [Start(s)] : H(a, s) | E(a, s, 0).
    ! a [Person(a)] : ! s [Start(s)] : ~H(a, s) | E(a, s, 1).
    ! a [Person(a)] : ! s [Start(s)] : ~E(a, s, 0) | ~H(a, s).
    ! a [Person(a)] : ! s [Start(s)] : ~E(a, s, 1) | H(a, s).
    ! a [Person(a)] : ! s [Start(s)] : ! c [Ge2(c)] : ~E(a, s, c).
    ! a [Person(a)] : ! p [Person(p)] : ! q [Next(q, p)] : ! c [Cnt(c)] : H(a, p) | ~E(a, q, c) | E(a, p, c).
    ! a [Person(a)] : ! p [Person(p)] : ! q [Next(q, p)] : ! c [Cnt(c)] : ! b [Prev(b, c)] : ~H(a, p) | ~E(a, q, b) | E(a, p, c).
    ! a [Person(a)] : ! p [Person(p)] : ~E(a, p, 0) | ~H(a, p).
    ! a [Person(a)] : ! p [Person(p)] : ! q [Next(q, p)] : ! c [Cnt(c)] : ~E(a, p, c) | H(a, p) | E(a, q, c).
    ! a [Person(a)] : ! p [Person(p)] : ! q [Next(q, p)] : ! c [Cnt(c)] : ! b [Prev(b, c)] : ~E(a, p, c) | ~H(a, p) | E(a, q, b).
    ! a [Asked(a)] : ! b [PairLt(a, b)] : ! l [Last(l)] : ! c [Cnt(c)] : ~E(a, l, c) | ~E(b, l, c).
    ! l [Last(l)] : ! d [Deg(d)] : ? a [Asked(a)] : E(a, l, d).
    ! l [Last(l)] : ! c [Cnt(c)] : ~E(0, l, c) | hil(c).
    ! l [Last(l)] : ! c [Cnt(c)] : ~hil(c) | E(0, l, c).
    ! l [Last(l)] : ! h [Hus(h)] : ! w [Spouse(h, w)] : ! c [Cnt(c)] : ! d [Le(c, d)] : ~E(h, l, c) | ~E(w, l, d).
    ! l [Last(l)] : ! h [Hus(h)] : ! g [NextH(h, g)] : ! c [Cnt(c)] : ! d [Le(c, d)] : ~E(h, l, c) | ~E(g, l, d).
}
"""


def structure(instance):
    n = instance["num_couples"]
    people = 2 * n + 2
    everyone = list(range(people))
    spouse = [(0, 1), (1, 0)]
    for k in range(1, n + 1):
        spouse += [(2 * k, 2 * k + 1), (2 * k + 1, 2 * k)]
    asked = [a for a in everyone if a != 1]
    pairs = [(a, b) for a in asked for b in asked if a < b]
    counts = list(range(people + 1))
    return {
        "domain": counts,
        "Person": everyone,
        "Asked": asked,
        "Spouse": spouse,
        "Cnt": counts,
        "Ge2": list(range(2, people + 1)),
        "Prev": [(c - 1, c) for c in range(1, people + 1)],
        "Start": [0],
        "Last": [people - 1],
        "Next": [(p, p + 1) for p in range(people - 1)],
        "PairLt": pairs,
        "Deg": list(range(2 * n + 1)),
        "Hus": [2 * k for k in range(1, n + 1)],
        "NextH": [(2 * k, 2 * k + 2) for k in range(1, n)],
        "Le": [(c, d) for c in counts for d in counts if c <= d],
    }
