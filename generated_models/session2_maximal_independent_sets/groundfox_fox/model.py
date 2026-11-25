# session2_maximal_independent_sets: a FOX model for GroundFOX from DCP Rosetta.
#
# In graph theory, an independent set is a set of vertices in a graph, no two of which are
# adjacent. A maximal independent set is an independent set that is not a subset of any other
# independent set. A graph may have many maximal independent sets of widely varying sizes:
# find a maximal independent set for the data provided. The data provides an array containing
# for each node of the graph the set of adjacent nodes.
#
# Print whether each node is included in the maximal independent set (nodes), as a list of
# booleans.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py session2_maximal_independent_sets.json --check

FOX = """
invocabulary { Node/1 Bool/1 Edge/2 }
outvocabulary { nodes/2 }
theory {
    ! i [Node(i)] : ? b [Bool(b)] : nodes(i, b).
    ! i [Node(i)] : ! b [Bool(b)] : ! c [Bool(c) & b ~= c] : ~nodes(i, b) | ~nodes(i, c).
    ! a [Node(a)] : ! b [Edge(a, b)] : ~nodes(a, 1) | ~nodes(b, 1).
    ! a [Node(a) & ~? b : Edge(a, b)] : nodes(a, 1).
    ! a [Node(a) & ? b : Edge(a, b)] : ? b [Edge(a, b)] : nodes(a, 1) | nodes(b, 1).
}
"""


def structure(instance):
    n = instance["n"]
    adj = instance["adjacency_list"]
    # Undirected edges, listed both ways; out-of-range entries and self-loops are ignored.
    edges = set()
    for i, row in enumerate(adj):
        for j in row:
            if isinstance(j, int) and 1 <= j <= n and j - 1 != i:
                edges.add((i, j - 1))
                edges.add((j - 1, i))
    return {
        "domain": list(range(max(n, 2) + 1)),
        "Node": list(range(n)),
        "Bool": [0, 1],
        "Edge": sorted(edges),
    }
