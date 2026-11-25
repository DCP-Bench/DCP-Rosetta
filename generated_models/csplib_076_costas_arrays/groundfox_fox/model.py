# csplib_076_costas_arrays: a FOX model for GroundFOX from DCP Rosetta.
#
# A Costas array is a pattern of \( n \) marks on an \( n \times n \) grid, one mark per row
# and one per column, in which the \( n \cdot (n-1)/2 \) vectors between the marks are all
# different. Such patterns are important as they provide a template for generating radar and
# sonar signals with ideal ambiguity functions.
#
# A model for Costas Array Problem (CAP) is to define an array of variables \( X_1, \ldots,
# X_n \) which form a permutation. For each length \( l \in \{1, \ldots, n-1\} \), we add \(
# n-l \) more variables \( X_{l1}, \ldots, X_{ln-1} \), whereby each of these variables is
# assigned the difference of \( X_i - X_{i+l} \) for \( i \in \{1, \ldots, n-l\} \). These
# additional variables form a difference triangle.
#
# Each line of this difference triangle must not contain any value twice. That is, the CAP is
# simply a collection of all-different constraints on \( X_1, \ldots, X_n \) and \( X_{l1},
# \ldots, X_{ln-l} \) for all \( l \in \{1, \ldots, n-1\} \).
#
# Print the Costas array (costas) as a list of n integers, 1-based indexing.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_076_costas_arrays.json --check

# csplib_076_costas_arrays: a FOX model for GroundFOX from DCP Rosetta.
#
# A Costas array of order n is a permutation X_1..X_n of 1..n such that, for every lag l=1..n-1,
# the differences X_i - X_{i+l} (i=1..n-l) are pairwise different. Print the permutation (costas),
# 1-based values, as a list of n integers.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Pos/1 Val/1 Dv/1 Sub/3 Ps/2 Pl/3 }
outvocabulary { costas/2 Dd/3 }
theory {
    ! i [Pos(i)] : ? v [Val(v)] : costas(i,v).
    ! i [Pos(i)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~costas(i,v) | ~costas(i,w).
    ! v [Val(v)] : ? i [Pos(i)] : costas(i,v).
    ! v [Val(v)] : ! i [Pos(i)] : ! j [Pos(j) & i ~= j] : ~costas(i,v) | ~costas(j,v).
    ! l : ! i [Ps(l,i)] : ? d [Dv(d)] : Dd(l,i,d).
    ! l : ! i [Ps(l,i)] : ! d [Dv(d)] : ! e [Dv(e) & d ~= e] : ~Dd(l,i,d) | ~Dd(l,i,e).
    ! l : ! i : ! j [Pl(l,i,j)] : ! v [Val(v)] : ! w [Val(w)] : ! d [Sub(v,w,d)] : ~costas(i,v) | ~costas(j,w) | Dd(l,i,d).
    ! l : ! i [Ps(l,i)] : ! k [Ps(l,k) & i ~= k] : ! d [Dv(d)] : ~Dd(l,i,d) | ~Dd(l,k,d).
}
"""


def structure(instance):
    n = instance["n"]
    # Position indices 0..n-1, values 1..n; difference v-w is shifted by n-1 to stay non-negative.
    return {
        "Pos": list(range(n)),
        "Val": list(range(1, n + 1)),
        "Dv": list(range(0, 2 * n - 1)),
        "Sub": [(v, w, v - w + n - 1) for v in range(1, n + 1) for w in range(1, n + 1) if v != w],
        "Ps": [(l, i) for l in range(1, n) for i in range(0, n - l)],
        "Pl": [(l, i, i + l) for l in range(1, n) for i in range(0, n - l)],
    }
