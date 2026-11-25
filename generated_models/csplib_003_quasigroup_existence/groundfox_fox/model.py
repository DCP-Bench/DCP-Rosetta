# csplib_003_quasigroup_existence: a FOX model for GroundFOX from DCP Rosetta.
#
# An order m quasigroup is a Latin square of size m. That is, a $m \times m$ multiplication
# table in which each element occurs once in every row and column. For example,
#
# ``` 1 2 3 4 4 1 2 3 3 4 1 2 2 3 4 1 ```
#
# is an order 4 quasigroup. A quasigroup can be specified by a set and a binary multiplication
# operator, \* defined over this set. Quasigroup existence problems determine the existence or
# non-existence of quasigroups of a given size with additional properties. Certain existence
# problems are of sufficient interest that a naming scheme has been invented for them. We
# define two new relations, \*321 and \*312 by $a \*321 b = c$ iff $c\*b=a$ and $a \*312 b =
# c$ iff $b\*c=a$.
#
# QG3.m problems are order m quasigroups for which $(a\*b)\*(b\*a) = a$. We only consider the
# QG3.m problem for this task.
#
# Print the quasigroup (quasigroup) as a list of lists of integers from 0 to m-1.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_003_quasigroup_existence.json --check

# csplib_003_quasigroup_existence: a FOX model for GroundFOX from DCP Rosetta.
#
# QG3.m: an order m quasigroup (Latin square) q with (a*b)*(b*a) = a for all a, b.
# Output quasigroup[i][j] = quasigroup(i, j).

FOX = """
invocabulary { Dom/1 }
outvocabulary { quasigroup/3 }
theory {
    ! i [Dom(i)] : ! j [Dom(j)] : ? v [Dom(v)] : quasigroup(i, j, v).
    ! i [Dom(i)] : ! j [Dom(j)] : ! v [Dom(v)] : ! w [Dom(w) & v ~= w] : ~quasigroup(i, j, v) | ~quasigroup(i, j, w).
    ! i [Dom(i)] : ! v [Dom(v)] : ! j [Dom(j)] : ! k [Dom(k) & j ~= k] : ~quasigroup(i, j, v) | ~quasigroup(i, k, v).
    ! j [Dom(j)] : ! v [Dom(v)] : ! i [Dom(i)] : ! k [Dom(k) & i ~= k] : ~quasigroup(i, j, v) | ~quasigroup(k, j, v).
    ! a [Dom(a)] : ! b [Dom(b)] : ! c [Dom(c)] : ! d [Dom(d)] : ~quasigroup(a, b, c) | ~quasigroup(b, a, d) | quasigroup(c, d, a).
}
"""


def structure(instance):
    m = instance["m"]
    dom = list(range(m))
    return {"Dom": dom, "domain": dom}
