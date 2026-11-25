# abbots_puzzle: a FOX model for GroundFOX from DCP Rosetta.
#
# If 100 bushels of corn were distributed among 100 people such that each man received three
# bushels, each woman two, and each child half a bushel, and there are five times as many
# women as men, find the number of men, women, and children.
#
# Print the number of men, women, and children (men, women, children).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py abbots_puzzle.json --check

FOX = """
invocabulary { Val/1 Five/2 Eq1/3 Eq2/3 }
outvocabulary { men/1 women/1 children/1 }
theory {
    ? v [Val(v)] : men(v).
    ! v [Val(v)] : ! u [Val(u) & v ~= u] : ~men(v) | ~men(u).
    ? v [Val(v)] : women(v).
    ! v [Val(v)] : ! u [Val(u) & v ~= u] : ~women(v) | ~women(u).
    ? v [Val(v)] : children(v).
    ! v [Val(v)] : ! u [Val(u) & v ~= u] : ~children(v) | ~children(u).
    ! m [Val(m)] : ! w [Val(w) & ~Five(m, w)] : ~men(m) | ~women(w).
    ! m [Val(m)] : ! w [Val(w) & ~? c : Eq1(m, w, c)] : ~men(m) | ~women(w).
    ! m [Val(m)] : ! w [Val(w) & ~? c : Eq2(m, w, c)] : ~men(m) | ~women(w).
    ! m [Val(m)] : ! w [Val(w)] : ! c [Eq1(m, w, c)] : ~men(m) | ~women(w) | children(c).
    ! m [Val(m)] : ! w [Val(w)] : ! c [Eq2(m, w, c)] : ~men(m) | ~women(w) | children(c).
}
"""


def structure(instance):
    # Statement constants: 100 people, 100 bushels; a man takes 3, a woman 2, a child 1/2.
    # Eq1: men + women + children = 100 people.
    # Eq2: 3*men + 2*women + children/2 = 100 bushels, doubled to stay in integers.
    # Five: five times as many women as men.
    people, bushels = 100, 200
    V = range(people + 1)
    return {
        "Val": list(V),
        "Five": [(m, 5 * m) for m in V if 5 * m <= people],
        "Eq1": [(m, w, people - m - w) for m in V for w in V if people - m - w >= 0],
        "Eq2": [(m, w, bushels - 6 * m - 4 * w) for m in V for w in V
                if 0 <= bushels - 6 * m - 4 * w <= people],
    }
