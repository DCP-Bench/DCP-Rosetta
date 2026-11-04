// Mario's route: Mario starts at his house, visits any subset of the houses, and ends at Luigi's house
// (the route closes with Luigi -> Mario). Maximise the gold collected, with total fuel at most fuelLimit.
// Output s[i] = the house after house i on the route, or i itself when house i is not on the route.
import org.jacop.constraints.*;
import org.jacop.core.*;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("nHouses");
        int mario = inst.getInt("marioHouse");
        int luigi = inst.getInt("luigiHouse");
        int fuelLimit = inst.getInt("fuelLimit");

        // Data from the instance. Staying in place costs no fuel, so the diagonal is set to 0.
        JSONArray goldJson = inst.getJSONArray("goldInHouse");
        JSONArray fuelJson = inst.getJSONArray("arc_fuel");
        int[] gold = new int[n];
        int[][] fuel = new int[n][n];
        int sumGold = 0;
        int maxArcFuel = 0;
        for (int i = 0; i < n; i++) {
            gold[i] = goldJson.getInt(i);
            sumGold += gold[i];
            for (int j = 0; j < n; j++) {
                fuel[i][j] = (i == j) ? 0 : fuelJson.getJSONArray(i).getInt(j);
                maxArcFuel = Math.max(maxArcFuel, fuel[i][j]);
            }
        }

        // next[i] = successor of house i on the route; next[i] == i means house i is skipped.
        IntVar[] next = new IntVar[n];
        for (int i = 0; i < n; i++) {
            next[i] = new IntVar(store, "next" + i, 0, n - 1);
        }
        // The successors form a permutation: every house has exactly one predecessor.
        store.impose(new Alldifferent(next));
        // Mario's house is on the route, and the route ends at Luigi's house, which returns to Mario.
        store.impose(new XneqC(next[mario], mario));
        store.impose(new XeqC(next[luigi], mario));

        // Skipped[i] = 1 when house i is not on the route (next[i] == i).
        BooleanVar[] skipped = new BooleanVar[n];
        for (int i = 0; i < n; i++) {
            skipped[i] = new BooleanVar(store, "skipped" + i);
            store.impose(new Reified(new XeqC(next[i], i), skipped[i]));
        }

        // No subtours: the route must be one path from Mario, not a cycle that misses Mario.
        // Miller-Tucker-Zemlin style position numbers: pos[mario] = 0, and each arc i -> j
        // that does not return to Mario increases the position by one. Only the arc into
        // Mario closes the route, so it is not constrained.
        IntVar[] pos = new IntVar[n];
        for (int i = 0; i < n; i++) {
            pos[i] = new IntVar(store, "pos" + i, 0, n - 1);
        }
        store.impose(new XeqC(pos[mario], 0));
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (i == j || j == mario) continue;
                BooleanVar arc = new BooleanVar(store, "arc" + i + "_" + j);
                store.impose(new Reified(new XeqC(next[i], j), arc));
                store.impose(new Implies(arc, new XplusCeqZ(pos[i], 1, pos[j])));
            }
        }

        // Fuel: fuelUsed[i] is the fuel of the arc leaving house i (0 when skipped).
        // The total must not exceed the fuel limit.
        IntVar[] fuelUsed = new IntVar[n];
        for (int i = 0; i < n; i++) {
            fuelUsed[i] = new IntVar(store, "fuelUsed" + i, 0, maxArcFuel);
            store.impose(Element.choose(next[i], fuel[i], fuelUsed[i], -1));
        }
        int[] ones = new int[n];
        for (int i = 0; i < n; i++) ones[i] = 1;
        store.impose(new LinearInt(fuelUsed, ones, "<=", fuelLimit));

        // Gold collected: the houses on the route, i.e. those not skipped.
        // goldTotal + sum(gold[i] * skipped[i]) = sumGold.
        IntVar goldTotal = new IntVar(store, 0, sumGold);
        IntVar[] goldVars = new IntVar[n + 1];
        int[] goldWeights = new int[n + 1];
        for (int i = 0; i < n; i++) {
            goldVars[i] = skipped[i];
            goldWeights[i] = gold[i];
        }
        goldVars[n] = goldTotal;
        goldWeights[n] = 1;
        store.impose(new LinearInt(goldVars, goldWeights, "==", sumGold));

        // Search over the successors first; the auxiliary variables follow.
        Model m = new Model().put("s", next);
        m.search(next, null, null);
        return m.maximize(goldTotal);
    }
}
