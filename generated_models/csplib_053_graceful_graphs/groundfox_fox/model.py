# csplib_053_graceful_graphs: a FOX model for GroundFOX from DCP Rosetta.
#
# A labelling \( f \) of the nodes of a graph with \( q \) edges is graceful if \( f \)
# assigns each node a unique label from \( \{0, 1, \ldots, q\} \) and when each edge \( xy \)
# is labelled with \( |f(x) - f(y)| \), the edge labels are all different. Gallian surveys
# graceful graphs, i.e., graphs with a graceful labelling, and lists the graphs whose status
# is known.
#
# Print the node labels (nodes) and the edge labels (edges), the latter in the order of the
# edges in `graph`.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_053_graceful_graphs.json --check

"""csplib_053_graceful_graphs: a FOX model for GroundFOX from DCP Rosetta.

nodes(x, v): node x gets label v in 0..q (q = number of edges). edges(e, l): edge e
has label l in 1..q. Each edge label is forced to |f(x) - f(y)| by a data relation
AD(u, v, l) over label pairs; node labels are injective and edge labels are distinct.
Node indices in the graph are shifted to 0-based when the instance uses 1-based ones.
"""

FOX = """
invocabulary { Node/1 Edge/1 Lbl/1 Lbl1/1 EE/3 AD/3 }
outvocabulary { nodes/2 edges/2 }
theory {
    ! x [Node(x)] : ? v [Lbl(v)] : nodes(x, v).
    ! x [Node(x)] : ! v [Lbl(v)] : ! w [Lbl(w) & v ~= w] : ~nodes(x, v) | ~nodes(x, w).
    ! x [Node(x)] : ! y [Node(y) & x ~= y] : ! v [Lbl(v)] : ~nodes(x, v) | ~nodes(y, v).
    ! e [Edge(e)] : ? l [Lbl1(l)] : edges(e, l).
    ! e [Edge(e)] : ! l [Lbl1(l)] : ! k [Lbl1(k) & l ~= k] : ~edges(e, l) | ~edges(e, k).
    ! e [Edge(e)] : ! x [Node(x)] : ! y [EE(e, x, y)] : ! u [Lbl(u)] : ! v [Lbl(v)] : ! l [AD(u, v, l)] : ~nodes(x, u) | ~nodes(y, v) | edges(e, l).
    ! e [Edge(e)] : ! f [Edge(f) & e ~= f] : ! l [Lbl1(l)] : ~edges(e, l) | ~edges(f, l).
}
"""


def structure(instance):
    g = [tuple(edge) for edge in instance["graph"]]
    m = len(g)
    n = instance["n"]
    base = 0 if any(0 in edge for edge in g) else 1
    q = m
    return {
        "Node": range(n),
        "Edge": range(m),
        "Lbl": range(q + 1),
        "Lbl1": range(1, q + 1),
        "EE": [(e, a - base, b - base) for e, (a, b) in enumerate(g)],
        "AD": [(u, v, abs(u - v)) for u in range(q + 1) for v in range(q + 1) if u != v],
    }
