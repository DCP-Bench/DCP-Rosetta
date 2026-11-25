# csplib_044_steiner: a FOX model for GroundFOX from DCP Rosetta.
#
# The ternary Steiner problem of order \( n \) consists of finding a set of \( n \cdot (n-1)/6
# \) triples of distinct integer elements in \(\{1, \ldots, n\}\) such that any two triples
# have at most one common element. It is a hypergraph problem coming from combinatorial
# mathematics where \( n \) modulo 6 has to be equal to 1 or 3. One possible solution for \( n
# = 7 \) is \(\{\{1, 2, 3\}, \{1, 4, 5\}, \{1, 6, 7\}, \{2, 4, 6\}, \{2, 5, 7\}, \{3, 4, 7\},
# \{3, 5, 6\}\}\). The solution contains \( 7 \cdot (7-1)/6 = 7 \) triples. This is a
# particular case of the more general Steiner system.
#
# Print the set of triples (sets) as a boolean matrix where each row represents a triple and
# each column represents an element. The value of the matrix at position [i, j] is true if
# element j is part of triple i, and false otherwise.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_044_steiner.json --check

# csplib_044_steiner: a FOX model for GroundFOX from DCP Rosetta.
#
# Ternary Steiner system of order n: T = n(n-1)/6 triples of distinct elements of 0..n-1,
# any two triples sharing at most one element. Output sets[r][a] is true when element a is in
# triple r. Each triple is given by three pick(r,k,a) choices (k = 0,1,2).
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Row/1 Col/1 K/1 }
outvocabulary { sets/3 pick/3 }
theory {
    ! r [Row(r)] : ! a [Col(a)] : sets(r,a,0) | sets(r,a,1).
    ! r [Row(r)] : ! a [Col(a)] : ~sets(r,a,0) | ~sets(r,a,1).
    ! r [Row(r)] : ! a [Col(a)] : ~sets(r,a,1) | pick(r,0,a) | pick(r,1,a) | pick(r,2,a).
    ! r [Row(r)] : ! a [Col(a)] : ~pick(r,0,a) | sets(r,a,1).
    ! r [Row(r)] : ! a [Col(a)] : ~pick(r,1,a) | sets(r,a,1).
    ! r [Row(r)] : ! a [Col(a)] : ~pick(r,2,a) | sets(r,a,1).
    ! r [Row(r)] : ! k [K(k)] : ? a [Col(a)] : pick(r,k,a).
    ! r [Row(r)] : ! a [Col(a)] : ! k [K(k)] : ! l [K(l) & k ~= l] : ~pick(r,k,a) | ~pick(r,l,a).
    ! r [Row(r)] : ! k [K(k)] : ! a [Col(a)] : ! b [Col(b) & a ~= b] : ~pick(r,k,a) | ~pick(r,k,b).
    ! r [Row(r)] : ! s [Row(s) & r ~= s] : ! a [Col(a)] : ! b [Col(b) & a ~= b] : ~sets(r,a,1) | ~sets(r,b,1) | ~sets(s,a,1) | ~sets(s,b,1).
}
"""


def structure(instance):
    n = instance["n"]
    T = n * (n - 1) // 6
    return {
        "domain": list(range(max(n, T, 3))),
        "Row": list(range(T)),
        "Col": list(range(n)),
        "K": [0, 1, 2],
    }
