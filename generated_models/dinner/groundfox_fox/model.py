# dinner: a FOX model for GroundFOX from DCP Rosetta.
#
# My son came to me the other day and said, 'Dad, I need help with a math problem.' The
# problem went like this:
#
# * We're going out to dinner taking 1-6 grandparents, 1-10 parents and/or 1-40 children *
# Grandparents cost $3 for dinner, parents $2 and children $0.50 * There must be 20 total
# people at dinner and it must cost $20 * How many grandparents, parents and children are
# going to dinner?
#
# Print the number of grandparents, parents and children going to dinner (grandparents,
# parents, children).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py dinner.json --check

# dinner: a FOX model for GroundFOX from DCP Rosetta.

FOX = """
invocabulary { G/1 P/1 C/1 Tot/3 Cost/3 }
outvocabulary { grandparents/1 parents/1 children/1 }
theory {
    ? g [G(g)] : grandparents(g).
    ! g [G(g)] : ! h [G(h) & g ~= h] : ~grandparents(g) | ~grandparents(h).
    ? p [P(p)] : parents(p).
    ! p [P(p)] : ! q [P(q) & p ~= q] : ~parents(p) | ~parents(q).
    ? c [C(c)] : children(c).
    ! c [C(c)] : ! d [C(d) & c ~= d] : ~children(c) | ~children(d).
    ! g [G(g)] : ! p [P(p)] : ! c [C(c) & ~Tot(g, p, c)] : ~grandparents(g) | ~parents(p) | ~children(c).
    ! g [G(g)] : ! p [P(p)] : ! c [C(c) & ~Cost(g, p, c)] : ~grandparents(g) | ~parents(p) | ~children(c).
}
"""


def structure(instance):
    # Money in cents: grandparent 300, parent 200, child 50; total cost $20.
    G = range(1, 7)
    P = range(1, 11)
    C = range(1, 41)
    return {
        "G": G,
        "P": P,
        "C": C,
        "Tot": [(g, p, c) for g in G for p in P for c in C if g + p + c == 20],
        "Cost": [(g, p, c) for g in G for p in P for c in C if 300 * g + 200 * p + 50 * c == 2000],
    }
