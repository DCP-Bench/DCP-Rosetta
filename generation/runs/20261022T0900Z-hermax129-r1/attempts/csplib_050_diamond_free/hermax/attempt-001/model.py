from hermax.model import Model


def build(instance):
    n = instance["N"]

    m = Model()

    # Adjacency matrix: m[i][j] is True if there's an edge between i and j
    adj = m.bool_matrix("adj", n, n)

    # No self-loops: diagonal must be all False
    for i in range(n):
        m &= ~adj[i][i]

    # Symmetry: the graph is undirected, so adj[i][j] = adj[j][i]
    for i in range(n):
        for j in range(i + 1, n):
            m &= (adj[i][j] == adj[j][i])

    # Degree constraints
    degrees = []
    for i in range(n):
        # Degree of vertex i is the sum of edges incident to it
        degree = m.sum_var([adj[i][j] for j in range(n)])
        degrees.append(degree)

        # Each degree must be > 0 (no isolated vertices)
        m &= (degree > 0)

        # Each degree must be divisible by 3
        q_i = m.int(f"q_{i}", 0, n // 3)
        m &= (degree == 3 * q_i)

    # Sum of degrees must be divisible by 12
    # Sum of degrees = 2 * number of edges
    # So 2 * edges must be divisible by 12, i.e., edges divisible by 6
    total_degree = m.sum_var(degrees)
    q_total = m.int("q_total", 0, (n * n) // 6)
    m &= (total_degree == 12 * q_total)

    # No diamonds: for every set of 4 vertices, the induced subgraph has at most 4 edges
    # A diamond is 4 vertices with 5 or 6 edges (since max is 6 edges among 4 vertices: C(4,2)=6)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                for l in range(k + 1, n):
                    # Count edges in the induced subgraph on vertices {i, j, k, l}
                    edges_in_4 = (
                        adj[i][j] + adj[i][k] + adj[i][l] +
                        adj[j][k] + adj[j][l] +
                        adj[k][l]
                    )
                    # Diamond-free means at most 4 edges
                    m &= (edges_in_4 <= 4)

    return m, {"matrix": adj}
