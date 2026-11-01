// Money change: Alice gives Bob an amount using her available coins, using as few coins as possible.
// Instance fields: amount (the change to give), types_of_coins[i] (the value of coin type i),
// available_coins[i] (how many coins of type i Alice has). The number of coin types is read from the instance.
// Output coin_counts[i] = number of coins of type i given to Bob. Objective: minimise the total number of coins.
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int amount = inst.getInt("amount");
        JSONArray types = inst.getJSONArray("types_of_coins");
        JSONArray available = inst.getJSONArray("available_coins");
        int kinds = types.length();

        // coin_counts[i]: between 0 and the number of coins of type i that Alice has
        IntVar[] counts = new IntVar[kinds];
        int[] values = new int[kinds];
        int totalAvailable = 0;
        for (int i = 0; i < kinds; i++) {
            int avail = available.getInt(i);
            counts[i] = new IntVar(store, "coins_" + i, 0, avail);
            values[i] = types.getInt(i);
            totalAvailable += avail;
        }

        // the coins given add up to the amount of change: sum of value_i * count_i = amount
        store.impose(new LinearInt(counts, values, "==", amount));

        // total number of coins given, the objective to minimise
        IntVar total = new IntVar(store, 0, totalAvailable);
        IntVar[] withTotal = new IntVar[kinds + 1];
        int[] weights = new int[kinds + 1];
        for (int i = 0; i < kinds; i++) {
            withTotal[i] = counts[i];
            weights[i] = 1;
        }
        withTotal[kinds] = total;
        weights[kinds] = -1;
        store.impose(new LinearInt(withTotal, weights, "==", 0));

        return new Model().put("coin_counts", counts).minimize(total);
    }
}
