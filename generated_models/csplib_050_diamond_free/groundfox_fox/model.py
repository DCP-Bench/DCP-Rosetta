# csplib_050_diamond_free: a FOX model for GroundFOX from DCP Rosetta.
#
# Given a simple undirected graph \( G = (V, E) \), where \( V \) is the set of vertices and
# \( E \) the set of undirected edges, the edge \(\{u, v\}\) is in \( E \) if and only if
# vertex \( u \) is adjacent to vertex \( v \in G \). The graph is simple in that there are no
# loop edges, i.e., we have no edges of the form \(\{v, v\}\). Each vertex \( v \in V \) has a
# degree \( d_v \) i.e., the number of edges incident on that vertex. Consequently, a graph
# has a degree sequence \( d_1, \ldots, d_n \), where \( d_i \geq d_{i+1} \). A diamond is a
# set of four vertices in \( V \) such that there are at least five edges between those
# vertices. Conversely, a graph is diamond-free if it has no diamond as an induced subgraph,
# i.e., for every set of four vertices the number of edges between those vertices is at most
# four.
#
# In our problem, we have additional properties required of the degree sequences of the
# graphs, in particular, that the degree of each vertex is greater than zero (i.e., isolated
# vertices are disallowed), the degree of each vertex is divisible by 3, and the sum of the
# degrees is divisible by 12 (i.e., \(|E|\) is divisible by 6).
#
# The problem is then, for a given number of vertices, to find a simple diamond-free graph
# such that
#
# - Each degree \( d_i > 0 \) and \( d_i \) is divisible by 3 - The sum of the degrees is
# divisible by 12
#
# Print the adjacency matrix of the graph (matrix) as a list of lists of booleans.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_050_diamond_free.json --check

# csplib_050_diamond_free: a FOX model for GroundFOX from DCP Rosetta.
#
# Find a simple graph on N vertices with no induced diamond (no four vertices spanning
# five or more edges), every degree positive and divisible by 3, and degree sum
# divisible by 12. Output the adjacency matrix (matrix) as booleans.

# Degree of each vertex: prefix-count states St(v, i, c) over its neighbours 0..i-1.
# Degree sum modulo 12: residue states Rr(i, r) over the vertices 0..i-1.
_QUAD_PAIRS = [("a", "b"), ("a", "c"), ("a", "d"), ("b", "c"), ("b", "d"), ("c", "d")]

_LINES = [
    "! i [Vtx(i)] : ! j [Vtx(j)] : matrix(i, j, 0) | matrix(i, j, 1).",
    "! i [Vtx(i)] : ! j [Vtx(j)] : ~matrix(i, j, 0) | ~matrix(i, j, 1).",
    "! i [Vtx(i)] : ! j [Vtx(j)] : ~matrix(i, j, 1) | matrix(j, i, 1).",
    "! i [Vtx(i)] : matrix(i, i, 0).",
]
# A diamond is four vertices with five or six edges: forbid each set of five of the six pairs.
for _excl in range(len(_QUAD_PAIRS)):
    _lits = " | ".join(
        f"~matrix({x}, {y}, 1)" for k, (x, y) in enumerate(_QUAD_PAIRS) if k != _excl
    )
    _LINES.append(f"! a [Vtx(a)] : ! b [Lt(a, b)] : ! c [Lt(b, c)] : ! d [Lt(c, d)] : {_lits}.")

_LINES += [
    # degree states
    "! v [Vtx(v)] : ! i [Start(i)] : ! c [Start(c)] : St(v, i, c).",
    "! v [Vtx(v)] : ! i [Pref(i)] : ? c [Cnt(c)] : St(v, i, c).",
    "! v [Vtx(v)] : ! i [Pref(i)] : ! c [Cnt(c)] : ! d [Cnt(d) & c ~= d] : ~St(v, i, c) | ~St(v, i, d).",
    "! v [Vtx(v)] : ! i [Vtx(i)] : ! j [Next(i, j)] : ! c [Cnt(c)] : ! d [Succ(c, d)] : ~St(v, i, c) | ~matrix(v, i, 1) | St(v, j, d).",
    "! v [Vtx(v)] : ! i [Vtx(i)] : ! j [Next(i, j)] : ! c [Cnt(c)] : ~St(v, i, c) | matrix(v, i, 1) | St(v, j, c).",
    "! v [Vtx(v)] : ! l [Last(l)] : ! c [Bad(c)] : ~St(v, l, c).",
    # degree sum modulo 12
    "! i [Start(i)] : ! r [Start(r)] : Rr(i, r).",
    "! i [Pref(i)] : ? r [Res(r)] : Rr(i, r).",
    "! i [Pref(i)] : ! r [Res(r)] : ! r2 [Res(r2) & r ~= r2] : ~Rr(i, r) | ~Rr(i, r2).",
    "! i [Vtx(i)] : ! j [Next(i, j)] : ! r [Res(r)] : ! c [Cnt(c)] : ! r2 [Add12(r, c, r2)] : ! l [Last(l)] : ~Rr(i, r) | ~St(i, l, c) | Rr(j, r2).",
    "! l [Last(l)] : ! r [Bad12(r)] : ~Rr(l, r).",
]

FOX = (
    "invocabulary { Vtx/1 Pref/1 Cnt/1 Res/1 Start/1 Last/1 Bad/1 Bad12/1 Next/2 Succ/2 Lt/2 Add12/3 }\n"
    "outvocabulary { matrix/3 St/3 Rr/2 }\n"
    "theory {\n    " + "\n    ".join(_LINES) + "\n}\n"
)


def structure(instance):
    N = instance["N"]
    return {
        "domain": range(max(N, 12) + 2),
        "Vtx": range(N),
        "Pref": range(N + 1),
        "Cnt": range(N + 1),
        "Res": range(12),
        "Start": [0],
        "Last": [N],
        "Bad": [c for c in range(N + 1) if not (c > 0 and c % 3 == 0)],
        "Bad12": range(1, 12),
        "Next": [(i, i + 1) for i in range(N)],
        "Succ": [(c, c + 1) for c in range(N)],
        "Lt": [(i, j) for i in range(N) for j in range(i + 1, N)],
        "Add12": [(r, c, (r + c) % 12) for r in range(12) for c in range(N + 1)],
    }
