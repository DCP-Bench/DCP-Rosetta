// Graceful graphs (CSPLib 053): label the nodes of a graph with q = m edges by
// distinct values from {0..q} so that the edge labels |f(x) - f(y)| are all different.
// Output nodes: the node labels f(v). Output edges: the edge labels, one per edge in the
// order given by the instance.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.AbsXeqY;
import org.jacop.constraints.XplusYeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");             // number of nodes
        int q = inst.getInt("m");             // number of edges, the largest label
        JSONArray graph = inst.getJSONArray("graph");   // 0-based node pairs

        // A node label is drawn from {0..q}.
        IntVar[] nodes = new IntVar[n];
        for (int v = 0; v < n; v++) {
            nodes[v] = new IntVar(store, "f" + v, 0, q);
        }
        // Graceful labelling: every node gets a different label.
        store.impose(new Alldifferent(nodes));

        // Each edge label is |f(x) - f(y)|. The edge labels must be all different and,
        // with q edges, they take exactly the values 1..q (an edge label cannot be 0,
        // since the node labels are different).
        IntVar[] edges = new IntVar[q];
        for (int k = 0; k < q; k++) {
            int x = graph.getJSONArray(k).getInt(0);
            int y = graph.getJSONArray(k).getInt(1);

            // diff = f(x) - f(y), written as diff + f(y) = f(x).
            IntVar diff = new IntVar(store, "d" + k, -q, q);
            store.impose(new XplusYeqZ(nodes[y], diff, nodes[x]));

            // The edge label is the absolute value of the difference.
            edges[k] = new IntVar(store, "e" + k, 1, q);
            store.impose(new AbsXeqY(diff, edges[k]));
        }
        // Edge labels are all different (the "graceful" condition on edges).
        store.impose(new Alldifferent(edges));

        Model m = new Model().put("nodes", nodes).put("edges", edges);
        m.search(nodes, null, null);          // label the node labels first
        return m;
    }
}
