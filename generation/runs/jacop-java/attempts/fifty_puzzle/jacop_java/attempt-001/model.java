// Fifty puzzle: each dummy carries a number. Choose which dummies to knock over so that the
// numbers on the knocked-over dummies add up to exactly the target sum.
// dummies[i] = 1 if dummy i is knocked over. The number of dummies, their numbers and the
// target all come from the instance.

import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray valuesJson = inst.getJSONArray("values");
        int target = inst.getInt("target_sum");
        int n = valuesJson.length();

        int[] values = new int[n];
        for (int i = 0; i < n; i++) {
            values[i] = valuesJson.getInt(i);
        }

        // dummies[i] = 1 if dummy i is knocked over
        BooleanVar[] dummies = new BooleanVar[n];
        for (int i = 0; i < n; i++) {
            dummies[i] = new BooleanVar(store, "d" + i);
        }

        // the sum of the numbers on the knocked-over dummies is exactly the target sum
        store.impose(new LinearInt(dummies, values, "==", target));

        return new Model().put("dummies", dummies);
    }
}
