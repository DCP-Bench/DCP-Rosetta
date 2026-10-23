// 0-1 knapsack: choose which items to take. Item i has value values[i] and weight
// weights[i]; the total weight must not exceed the capacity, and the total value is
// maximised. Output x[i] is true when item i is taken. The number of items comes from
// the instance.
import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray valueList = inst.getJSONArray("values");
        JSONArray weightList = inst.getJSONArray("weights");
        int capacity = inst.getInt("capacity");
        int n = valueList.length();

        // take[i] is 1 when item i is in the backpack.
        BooleanVar[] take = new BooleanVar[n];
        int[] values = new int[n];
        int[] weights = new int[n];
        int totalValue = 0;
        for (int i = 0; i < n; i++) {
            take[i] = new BooleanVar(store, "take" + i);
            values[i] = valueList.getInt(i);
            weights[i] = weightList.getInt(i);
            totalValue += values[i];
        }

        // The total weight of the chosen items is at most the capacity.
        store.impose(new LinearInt(take, weights, "<=", capacity));

        // total is the total value of the chosen items: total = sum of values[i] * take[i].
        // The linking constraint puts total on the right with weight -1.
        IntVar total = new IntVar(store, 0, totalValue);
        IntVar[] linked = new IntVar[n + 1];
        int[] linkWeights = new int[n + 1];
        for (int i = 0; i < n; i++) {
            linked[i] = take[i];
            linkWeights[i] = values[i];
        }
        linked[n] = total;
        linkWeights[n] = -1;
        store.impose(new LinearInt(linked, linkWeights, "==", 0));

        // Output x says which items are taken; the objective is the total value.
        return new Model().put("x", take).maximize(total);
    }
}
