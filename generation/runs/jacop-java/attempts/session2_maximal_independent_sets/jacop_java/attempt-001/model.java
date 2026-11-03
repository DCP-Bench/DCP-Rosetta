// Maximal independent set: choose a set of nodes with no two adjacent, such that every node outside the set
// has a neighbour inside it (the set cannot be extended). Output nodes[i] is true when node i is in the set.
// The adjacency lists use 1-based node numbers.
import org.jacop.constraints.*;
import org.jacop.core.*;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        JSONArray adjacency = inst.getJSONArray("adjacency_list");

        // inSet[i] = 1 when node i (0-based) is in the independent set.
        BooleanVar[] inSet = new BooleanVar[n];
        for (int i = 0; i < n; i++) {
            inSet[i] = new BooleanVar(store, "inSet" + i);
        }

        // Independence: two adjacent nodes are not both in the set.
        for (int i = 0; i < n; i++) {
            JSONArray neighbours = adjacency.getJSONArray(i);
            for (int k = 0; k < neighbours.length(); k++) {
                int j = neighbours.getInt(k) - 1;
                store.impose(new LinearInt(new IntVar[]{inSet[i], inSet[j]}, new int[]{1, 1}, "<=", 1));
            }
        }

        // Maximality: a node not in the set has a neighbour in the set. Written for every node v as
        // inSet[v] + (number of neighbours of v in the set) >= 1, which covers both cases.
        for (int v = 0; v < n; v++) {
            JSONArray neighbours = adjacency.getJSONArray(v);
            IntVar[] closed = new IntVar[neighbours.length() + 1];
            int[] ones = new int[closed.length];
            closed[0] = inSet[v];
            ones[0] = 1;
            for (int k = 0; k < neighbours.length(); k++) {
                closed[k + 1] = inSet[neighbours.getInt(k) - 1];
                ones[k + 1] = 1;
            }
            store.impose(new LinearInt(closed, ones, ">=", 1));
        }

        return new Model().put("nodes", inSet);
    }
}
