// Subset sum with bags: a van held several kinds of coin bags, each kind holding a fixed
// number of coins. Some bags were stolen, and exactly total_coins_lost coins were lost.
// Find how many bags of each kind were stolen (bags[i] for coin kind i).
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // The coin kinds and the total lost come from the instance.
        JSONArray coinNumbers = inst.getJSONArray("coin_numbers");
        int total = inst.getInt("total_coins_lost");
        int kinds = coinNumbers.length();

        // bags[i] = number of bags of kind i that were stolen. A bag holds coinNumbers[i] coins,
        // so at most total / coinNumbers[i] bags of that kind can fit in the total.
        IntVar[] bags = new IntVar[kinds];
        int[] coins = new int[kinds];
        for (int i = 0; i < kinds; i++) {
            coins[i] = coinNumbers.getInt(i);
            int most = coins[i] > 0 ? total / coins[i] : total;
            bags[i] = new IntVar(store, 0, most);
        }

        // The stolen coins add up to exactly the number lost:
        // sum over kinds of bags[i] * coins[i] = total.
        store.impose(new LinearInt(bags, coins, "==", total));

        // Output: the number of stolen bags per kind. Labelling them fixes the outcome.
        Model m = new Model().put("bags", bags);
        return m.search(bags, null, null);
    }
}
