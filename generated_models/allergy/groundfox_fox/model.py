# allergy: a FOX model for GroundFOX from DCP Rosetta.
#
# Four friends (two women named Debra and Janet, and two men named Hugh and Rick) found that
# each of them is allergic to something different: eggs, mold, nuts and ragweed. We would like
# to match each one's surname (Baxter, Lemon, Malone and Fleet) with his or her allergy. We
# know that: - Rick is not allergic to mold - Baxter is allergic to eggs - Hugh is neither
# surnamed Lemon nor Fleet - Debra is allergic to ragweed - Janet (who isn't Lemon) is neither
# allergic to eggs nor to mold
#
# Print the values of each food (eggs, mold, nuts, ragweed) and surname (baxter, lemon,
# malone, fleet) for each friend, where Debra = 0, Janet = 1, Hugh = 2, Rick = 3.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py allergy.json --check

# allergy: a GroundFOX model. Friends are indexed Debra=0, Janet=1, Hugh=2, Rick=3.
# Each food and each surname is an integer-valued output giving the friend who has it.

FOX = """
invocabulary { Val/1 }
outvocabulary { eggs/1 mold/1 nuts/1 ragweed/1 baxter/1 lemon/1 malone/1 fleet/1 }
theory {
    ? v [Val(v)] : eggs(v).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~eggs(v) | ~eggs(w).
    ? v [Val(v)] : mold(v).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~mold(v) | ~mold(w).
    ? v [Val(v)] : nuts(v).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~nuts(v) | ~nuts(w).
    ? v [Val(v)] : ragweed(v).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~ragweed(v) | ~ragweed(w).
    ? v [Val(v)] : baxter(v).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~baxter(v) | ~baxter(w).
    ? v [Val(v)] : lemon(v).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~lemon(v) | ~lemon(w).
    ? v [Val(v)] : malone(v).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~malone(v) | ~malone(w).
    ? v [Val(v)] : fleet(v).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~fleet(v) | ~fleet(w).

    ! v [Val(v)] : ~eggs(v) | ~mold(v).
    ! v [Val(v)] : ~eggs(v) | ~nuts(v).
    ! v [Val(v)] : ~eggs(v) | ~ragweed(v).
    ! v [Val(v)] : ~mold(v) | ~nuts(v).
    ! v [Val(v)] : ~mold(v) | ~ragweed(v).
    ! v [Val(v)] : ~nuts(v) | ~ragweed(v).
    ! v [Val(v)] : ~baxter(v) | ~lemon(v).
    ! v [Val(v)] : ~baxter(v) | ~malone(v).
    ! v [Val(v)] : ~baxter(v) | ~fleet(v).
    ! v [Val(v)] : ~lemon(v) | ~malone(v).
    ! v [Val(v)] : ~lemon(v) | ~fleet(v).
    ! v [Val(v)] : ~malone(v) | ~fleet(v).

    ! v [Val(v)] : ~eggs(v) | baxter(v).
    ! u [u = 3] : ~mold(3).
    ! u [u = 2] : ~lemon(2).
    ! u [u = 2] : ~fleet(2).
    ! u [u = 0] : ragweed(0).
    ! u [u = 1] : ~lemon(1).
    ! u [u = 1] : ~eggs(1).
    ! u [u = 1] : ~mold(1).
}
"""


def structure(instance):
    return {"Val": range(4)}
