// Coin selection: choose how many coins of each denomination to use so that every
// amount from 1 up to (but not including) max_amount_to_pay can be paid exactly
// with those coins, using as few coins in total as possible.

import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Instance data: denominations[j] is the value of coin type j, and every
        // amount a with 1 <= a < max_amount_to_pay must be payable.
        JSONArray denomJson = inst.getJSONArray("denominations");
        int maxAmount = inst.getInt("max_amount_to_pay");
        int types = denomJson.length();

        int[] denom = new int[types];
        for (int j = 0; j < types; j++) {
            denom[j] = denomJson.getInt(j);
        }

        // x[j] = number of coins of type j used (the declared output).
        // A solution never needs more than maxAmount - 1 coins of one type,
        // since any single payment uses at most that many of it.
        IntVar[] x = new IntVar[types];
        for (int j = 0; j < types; j++) {
            x[j] = new IntVar(store, "x_" + j, 0, Math.max(maxAmount - 1, 0));
        }

        // Total number of coins, the objective to minimise.
        int coinBound = types * Math.max(maxAmount - 1, 0);
        IntVar total = new IntVar(store, "total_coins", 0, coinBound);
        IntVar[] totalVars = new IntVar[types + 1];
        int[] totalWeights = new int[types + 1];
        for (int j = 0; j < types; j++) {
            totalVars[j] = x[j];
            totalWeights[j] = 1;
        }
        totalVars[types] = total;
        totalWeights[types] = -1;
        store.impose(new LinearInt(totalVars, totalWeights, "==", 0));

        // For every amount a to pay, y[j] = number of coins of type j used to pay a.
        // Constraints per amount:
        //   - the coins used to pay a add up to exactly a;
        //   - a payment uses no more coins of a type than are available: y[j] <= x[j].
        for (int a = 1; a < maxAmount; a++) {
            IntVar[] y = new IntVar[types];
            for (int j = 0; j < types; j++) {
                // A coin of type j can appear at most a / denom[j] times in a payment of a.
                int maxUse = a / denom[j];
                y[j] = new IntVar(store, "y_" + a + "_" + j, 0, maxUse);
            }

            // Value of the coins used to pay a equals a.
            store.impose(new LinearInt(y, denom, "==", a));

            // Each type used in this payment is available in the purse.
            for (int j = 0; j < types; j++) {
                IntVar[] pair = {y[j], x[j]};
                int[] pairWeights = {1, -1};
                store.impose(new LinearInt(pair, pairWeights, "<=", 0));
            }
        }

        // Labels the coin counts first; the per-amount payment variables follow.
        return new Model()
                .put("x", x)
                .search(x, null, null)
                .minimize(total);
    }
}
