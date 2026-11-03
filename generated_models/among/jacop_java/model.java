// Among: exactly m entries of the array x take a value from the set v.
// The array has n entries; each entry ranges over 0..7 (the problem's fixed value range).
// Entries are not otherwise restricted; only the count of entries in v is fixed to m.

import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Max;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");          // length of x, from the instance
        int m = inst.getInt("m");          // exact number of entries of x that must be in v
        JSONArray vj = inst.getJSONArray("v");
        int k = vj.length();               // size of the value set v

        // x[i] in 0..7: the problem's fixed value range
        IntVar[] x = new IntVar[n];
        for (int i = 0; i < n; i++) {
            x[i] = new IntVar(store, "x" + i, 0, 7);
        }

        // inV[i] = 1 if x[i] takes one of the values in v, else 0
        BooleanVar[] inV = new BooleanVar[n];
        for (int i = 0; i < n; i++) {
            inV[i] = new BooleanVar(store, "inV" + i);
            if (k == 0) {
                // v is empty: no entry can be in v
                store.impose(new XeqC(inV[i], 0));
                continue;
            }
            // eq[i][j] = 1 if x[i] equals the j-th value of v
            BooleanVar[] eq = new BooleanVar[k];
            for (int j = 0; j < k; j++) {
                eq[j] = new BooleanVar(store, "eq" + i + "_" + j);
                store.impose(new Reified(new XeqC(x[i], vj.getInt(j)), eq[j]));
            }
            // inV[i] is the maximum of the eq flags: 1 when any of them is 1.
            // (A max, not a sum, so a value repeated in v is not counted twice.)
            store.impose(new Max(eq, inV[i]));
        }

        // exactly m entries of x are in v
        int[] ones = new int[n];
        for (int i = 0; i < n; i++) ones[i] = 1;
        store.impose(new LinearInt(inV, ones, "==", m));

        Model model = new Model();
        return model.put("x", x);
    }
}
