// Bus driver scheduling (CSPLib 022): choose a subset of shifts so that every piece of
// work is covered by exactly one chosen shift. Minimise the number of chosen shifts.
// Model: one Boolean per shift (x[s] = 1 if shift s is selected), an exact-cover
// constraint per piece of work, and a total count that is minimised.
// Work and shift indices in the data are 0-based, as in the instance file.

import org.jacop.constraints.LinearInt;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XeqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int numWork = inst.getInt("num_work");
        JSONArray shifts = inst.getJSONArray("shifts");
        int m = shifts.length();

        // x[s] = 1 if shift s is selected in the schedule
        BooleanVar[] x = new BooleanVar[m];
        IntVar[] xs = new IntVar[m];
        for (int s = 0; s < m; s++) {
            x[s] = new BooleanVar(store, "x" + s);
            xs[s] = x[s];
        }

        // every piece of work t is covered by exactly one selected shift:
        // the sum of x[s] over the shifts s that contain t equals 1
        for (int t = 0; t < numWork; t++) {
            java.util.ArrayList<IntVar> covering = new java.util.ArrayList<>();
            for (int s = 0; s < m; s++) {
                JSONArray row = shifts.getJSONArray(s);
                for (int k = 0; k < row.length(); k++) {
                    if (row.getInt(k) == t) {
                        covering.add(x[s]);
                        break;
                    }
                }
            }
            if (covering.isEmpty()) {
                // no shift covers this work: the exact cover is impossible
                store.impose(new XeqC(new IntVar(store, 0, 0), 1));
            } else {
                int[] ones = new int[covering.size()];
                java.util.Arrays.fill(ones, 1);
                store.impose(new LinearInt(covering.toArray(new IntVar[0]), ones, "==", 1));
            }
        }

        // objective: the number of selected shifts (all shifts cost the same)
        IntVar total = new IntVar(store, 0, m);
        store.impose(new SumInt(xs, "==", total));

        return new Model().put("x", x).minimize(total);
    }
}
