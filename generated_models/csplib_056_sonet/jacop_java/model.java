// SONET (CSPLib 056): place nodes on rings so that every communicating pair
// shares a ring, each ring holds at most its capacity of nodes, and the total
// number of add-drop multiplexers (one per node per ring it is on) is minimal.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XplusYeqZ;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");          // number of nodes, from the instance
        int r = inst.getInt("r");          // number of rings, from the instance
        JSONArray demand = inst.getJSONArray("demand");
        JSONArray capacity = inst.getJSONArray("capacity_nodes");

        // on[k][i] = 1 if node i is installed on ring k (ring_config, output)
        BooleanVar[][] on = new BooleanVar[r][n];
        for (int k = 0; k < r; k++)
            for (int i = 0; i < n; i++)
                on[k][i] = new BooleanVar(store, "on_" + k + "_" + i);

        int[] ones = new int[n];
        java.util.Arrays.fill(ones, 1);

        // ring capacity: the number of nodes on ring k is at most capacity_nodes[k]
        for (int k = 0; k < r; k++)
            store.impose(new LinearInt(on[k], ones, "<=", capacity.getInt(k)));

        // communication: a pair with nonzero demand (either direction) must share a ring.
        // For each pair and ring, share[k] <-> both nodes are on ring k.
        // The pair is served when at least one share[k] holds.
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (demand.getJSONArray(i).getInt(j) == 0 && demand.getJSONArray(j).getInt(i) == 0)
                    continue;
                BooleanVar[] share = new BooleanVar[r];
                for (int k = 0; k < r; k++) {
                    // both = on[k][i] + on[k][j], which is 2 exactly when both are on ring k
                    IntVar both = new IntVar(store, 0, 2);
                    store.impose(new XplusYeqZ(on[k][i], on[k][j], both));
                    share[k] = new BooleanVar(store, "share_" + k + "_" + i + "_" + j);
                    store.impose(new Reified(new XeqC(both, 2), share[k]));
                }
                // at least one ring hosts both nodes
                int[] ones_r = new int[r];
                java.util.Arrays.fill(ones_r, 1);
                store.impose(new LinearInt(share, ones_r, ">=", 1));
            }
        }

        // objective: total number of ADMs, i.e. the number of (node, ring) installations
        BooleanVar[] all = new BooleanVar[r * n];
        for (int k = 0; k < r; k++)
            for (int i = 0; i < n; i++)
                all[k * n + i] = on[k][i];
        IntVar total = new IntVar(store, 0, r * n);
        store.impose(new SumInt(all, "==", total));

        return new Model().put("ring_config", on).put("total_adms", total).minimize(total);
    }
}
