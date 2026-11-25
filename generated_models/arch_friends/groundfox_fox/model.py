# arch_friends: a FOX model for GroundFOX from DCP Rosetta.
#
# Harriet, upon returning from the mall, is happily describing her four shoe purchases to her
# friend Aurora. Aurora just loves the four different kinds of shoes that Harriet bought (ecru
# espadrilles, fuchsia flats, purple pumps, and suede sandals), but Harriet can't recall at
# which different store (Foot Farm, Heels in a Handcart, The Shoe Palace, or Tootsies) she got
# each pair. Can you help these two figure out the order in which Harriet bought each pair of
# shoes, and where she bought each?
#
# 1. Harriet bought fuchsia flats at Heels in a Handcart. 2. The store she visited just after
# buying her purple pumps was not Tootsies. 3. The Foot Farm was Harriet's second stop. 4. Two
# stops after leaving The Shoe Palace, Harriet bought her suede sandals.
#
# Print the values of each shoe (ecruespadrilles, fuchsiaflats, purplepumps, suedesandals) and
# store (footfarm, heelsinahandcart, theshoepalace, tootsies), where each value is the number
# of the stop, from 1 to 4, at which that shoe was bought or that store was visited.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py arch_friends.json --check

FOX = """
invocabulary { Val/1 Next/2 Two/2 }
outvocabulary {
    ecruespadrilles/1 fuchsiaflats/1 purplepumps/1 suedesandals/1
    footfarm/1 heelsinahandcart/1 theshoepalace/1 tootsies/1
}
theory {
    ? v [Val(v)] : ecruespadrilles(v).
    ? v [Val(v)] : fuchsiaflats(v).
    ? v [Val(v)] : purplepumps(v).
    ? v [Val(v)] : suedesandals(v).
    ? v [Val(v)] : footfarm(v).
    ? v [Val(v)] : heelsinahandcart(v).
    ? v [Val(v)] : theshoepalace(v).
    ? v [Val(v)] : tootsies(v).

    ! v [Val(v)] : ! w [Val(w) & ~(v = w)] : ~ecruespadrilles(v) | ~ecruespadrilles(w).
    ! v [Val(v)] : ! w [Val(w) & ~(v = w)] : ~fuchsiaflats(v) | ~fuchsiaflats(w).
    ! v [Val(v)] : ! w [Val(w) & ~(v = w)] : ~purplepumps(v) | ~purplepumps(w).
    ! v [Val(v)] : ! w [Val(w) & ~(v = w)] : ~suedesandals(v) | ~suedesandals(w).
    ! v [Val(v)] : ! w [Val(w) & ~(v = w)] : ~footfarm(v) | ~footfarm(w).
    ! v [Val(v)] : ! w [Val(w) & ~(v = w)] : ~heelsinahandcart(v) | ~heelsinahandcart(w).
    ! v [Val(v)] : ! w [Val(w) & ~(v = w)] : ~theshoepalace(v) | ~theshoepalace(w).
    ! v [Val(v)] : ! w [Val(w) & ~(v = w)] : ~tootsies(v) | ~tootsies(w).

    ! v [Val(v)] : ~ecruespadrilles(v) | ~fuchsiaflats(v).
    ! v [Val(v)] : ~ecruespadrilles(v) | ~purplepumps(v).
    ! v [Val(v)] : ~ecruespadrilles(v) | ~suedesandals(v).
    ! v [Val(v)] : ~fuchsiaflats(v) | ~purplepumps(v).
    ! v [Val(v)] : ~fuchsiaflats(v) | ~suedesandals(v).
    ! v [Val(v)] : ~purplepumps(v) | ~suedesandals(v).
    ! v [Val(v)] : ~footfarm(v) | ~heelsinahandcart(v).
    ! v [Val(v)] : ~footfarm(v) | ~theshoepalace(v).
    ! v [Val(v)] : ~footfarm(v) | ~tootsies(v).
    ! v [Val(v)] : ~heelsinahandcart(v) | ~theshoepalace(v).
    ! v [Val(v)] : ~heelsinahandcart(v) | ~tootsies(v).
    ! v [Val(v)] : ~theshoepalace(v) | ~tootsies(v).

    ! v [Val(v)] : ~fuchsiaflats(v) | heelsinahandcart(v).
    ! v [Val(v)] : ! w [Next(v, w)] : ~purplepumps(v) | ~tootsies(w).
    ! u [u = 2] : footfarm(2).
    ! v [Val(v)] : ! w [Val(w) & ~Two(v, w)] : ~theshoepalace(v) | ~suedesandals(w).
}
"""


def structure(instance):
    stops = [1, 2, 3, 4]
    return {
        "Val": stops,
        "Next": [(a, a + 1) for a in stops if a + 1 in stops],
        "Two": [(a, a + 2) for a in stops if a + 2 in stops],
    }
