# csplib_067_quasigroup_completion: a FOX model for GroundFOX from DCP Rosetta.
#
# An order m quasigroup is a Latin square of size m. That is, an m x m multiplication table in
# which each element from 1 to m occurs exactly once in every row and every column. This
# problem asks to complete a partially filled quasigroup, given as `start`, in which 0 marks
# an empty cell.
#
# Print the completed quasigroup (puzzle) as a list of lists of integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_067_quasigroup_completion.json --check

# csplib_067_quasigroup_completion: a FOX model for GroundFOX from DCP Rosetta.
#
# Complete a partially filled order-N quasigroup (Latin square): every row and every column
# holds each value 1..N exactly once. The start grid gives the clues (0 marks an empty cell).
# Cells and values are 0-based indices and 1-based values, as the description and brief say.

def _theory():
    return (
        "invocabulary { Idx/1 Val/1 Given/3 }\n"
        "outvocabulary { puzzle/3 }\n"
        "theory {\n"
        "    ! r [Idx(r)] : ! c [Idx(c)] : ? v [Val(v)] : puzzle(r, c, v).\n"
        "    ! r [Idx(r)] : ! c [Idx(c)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : "
        "~puzzle(r, c, v) | ~puzzle(r, c, w).\n"
        "    ! r [Idx(r)] : ! v [Val(v)] : ! c [Idx(c)] : ! d [Idx(d) & c ~= d] : "
        "~puzzle(r, c, v) | ~puzzle(r, d, v).\n"
        "    ! c [Idx(c)] : ! v [Val(v)] : ! r [Idx(r)] : ! s [Idx(s) & r ~= s] : "
        "~puzzle(r, c, v) | ~puzzle(s, c, v).\n"
        "    ! r [Idx(r)] : ! c [Idx(c)] : ! v [Given(r, c, v)] : puzzle(r, c, v).\n"
        "}\n"
    )


FOX = _theory()


def structure(instance):
    n = instance["N"]
    start = instance["start"]
    given = [
        (r, c, start[r][c])
        for r in range(n)
        for c in range(n)
        if start[r][c] != 0
    ]
    return {
        "domain": range(0, n + 1),
        "Idx": range(n),
        "Val": range(1, n + 1),
        "Given": given,
    }
