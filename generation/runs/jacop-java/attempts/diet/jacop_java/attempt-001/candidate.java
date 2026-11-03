// Diet problem: choose how many units of each food to buy so that the nutrient totals reach
// at least the required minimum for each nutrient, at the lowest total price.
// Foods, in order: chocolate cake (1 slice), chocolate ice cream (1 scoop), cola (1 bottle),
// pineapple cheesecake (1 piece). The nutrient table below is the problem's own data.
// Nutrient order in the instance limits: calories, chocolate (ounces), sugar (ounces), fat (ounces).
// Prices and limits come from the instance; the number of foods is n from the instance.

import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    // amount of each nutrient per unit of each food, as described in the problem
    static final int[][] NUTRIENTS = {
        {400, 200, 150, 500},  // calories
        {3, 2, 0, 0},          // chocolate (ounces)
        {2, 2, 4, 4},          // sugar (ounces)
        {2, 4, 1, 5},          // fat (ounces)
    };

    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");                // number of foods
        JSONArray priceJson = inst.getJSONArray("price");
        JSONArray limitJson = inst.getJSONArray("limits");

        int[] price = new int[n];
        for (int i = 0; i < n; i++) {
            price[i] = priceJson.getInt(i);
        }
        int[] limits = new int[NUTRIENTS.length];
        for (int j = 0; j < NUTRIENTS.length; j++) {
            limits[j] = limitJson.getInt(j);
        }

        // units bought of each food; an upper bound of the sum of the requirements is generous
        // for every food, since the requirements are minimums and no food is needed beyond them
        int units = 0;
        for (int limit : limits) {
            units += limit;
        }
        IntVar[] x = new IntVar[n];
        for (int i = 0; i < n; i++) {
            x[i] = new IntVar(store, 0, units);
        }

        // each nutrient total is at least its required minimum
        for (int j = 0; j < NUTRIENTS.length; j++) {
            store.impose(new LinearInt(x, NUTRIENTS[j], ">=", limits[j]));
        }

        // cost = sum of price[i] * x[i]: the objective variable is fixed by a linear equation
        long upper = 0;
        for (int i = 0; i < n; i++) {
            upper += (long) price[i] * units;
        }
        IntVar cost = new IntVar(store, 0, (int) upper);
        IntVar[] vars = new IntVar[n + 1];
        int[] weights = new int[n + 1];
        for (int i = 0; i < n; i++) {
            vars[i] = x[i];
            weights[i] = price[i];
        }
        vars[n] = cost;
        weights[n] = -1;
        store.impose(new LinearInt(vars, weights, "==", 0));

        return new Model().put("cost", cost).minimize(cost);
    }
}
