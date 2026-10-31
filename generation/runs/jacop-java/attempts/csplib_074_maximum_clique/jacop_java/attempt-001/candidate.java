// Maximum clique: choose a set of vertices of an undirected graph (n vertices, adjacency matrix adj)
// such that every two chosen vertices are adjacent, and make the set as large as possible.
// Output c[i] = 1 if vertex i is in the clique, 0 otherwise.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.SumInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        JSONArray adj = inst.getJSONArray("adj");

        // c[i] = 1 if vertex i is in the clique.
        IntVar[] c = new IntVar[n];
        for (int i = 0; i < n; i++) {
            c[i] = new BooleanVar(store, "c_" + i);
        }

        // Two distinct vertices that are not adjacent cannot both be in the clique.
        // The graph is undirected; a pair is non-adjacent if either entry says so.
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                boolean adjacent = adj.getJSONArray(i).getInt(j) != 0
                        && adj.getJSONArray(j).getInt(i) != 0;
                if (!adjacent) {
                    store.impose(new LinearInt(new IntVar[]{c[i], c[j]}, new int[]{1, 1}, "<=", 1));
                }
            }
        }

        // Clique size: the number of chosen vertices, which is maximised.
        IntVar size = new IntVar(store, "size", 0, n);
        store.impose(new SumInt(c, "==", size));

        // Label the membership variables first; they decide the output.
        return new Model().put("c", c).maximize(size).search(c, null, null);
    }
}
