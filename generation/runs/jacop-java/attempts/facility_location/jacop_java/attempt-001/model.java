// Facility location: choose which warehouses to open (fixed cost each) and how many units
// each open warehouse ships to each region, so that every region gets its demand, no
// warehouse ships more than max_shipping, and the total cost is minimal.
// Warehouse order follows warehouse_s: 0 New York, 1 Los Angeles, 2 Chicago, 3 Atlanta.
import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray fixedCosts = inst.getJSONArray("fixed_costs");   // one per warehouse
        JSONArray demands = inst.getJSONArray("demands");          // one per region
        JSONArray shippingCosts = inst.getJSONArray("shipping_costs");
        int maxShipping = inst.getInt("max_shipping");
        int nW = fixedCosts.length();
        int nR = demands.length();

        // open[i] = 1 if warehouse i is open
        BooleanVar[] open = new BooleanVar[nW];
        for (int i = 0; i < nW; i++)
            open[i] = new BooleanVar(store, "open_" + i);

        // ships[i][j] = units shipped from warehouse i to region j
        IntVar[][] ships = new IntVar[nW][nR];
        for (int i = 0; i < nW; i++)
            for (int j = 0; j < nR; j++)
                ships[i][j] = new IntVar(store, 0, maxShipping);

        int[] ones = new int[Math.max(nW, nR)];
        java.util.Arrays.fill(ones, 1);

        // every region receives exactly its demand
        for (int j = 0; j < nR; j++) {
            IntVar[] col = new IntVar[nW];
            for (int i = 0; i < nW; i++)
                col[i] = ships[i][j];
            store.impose(new LinearInt(col, java.util.Arrays.copyOf(ones, nW), "==", demands.getInt(j)));
        }

        // a warehouse ships at most max_shipping in total, and nothing when it is closed:
        // sum_j ships[i][j] - max_shipping * open[i] <= 0
        for (int i = 0; i < nW; i++) {
            IntVar[] vars = new IntVar[nR + 1];
            int[] w = new int[nR + 1];
            for (int j = 0; j < nR; j++) {
                vars[j] = ships[i][j];
                w[j] = 1;
            }
            vars[nR] = open[i];
            w[nR] = -maxShipping;
            store.impose(new LinearInt(vars, w, "<=", 0));
        }

        // restriction 1: if New York is open then Los Angeles is open
        store.impose(new LinearInt(new IntVar[]{open[0], open[1]}, new int[]{1, -1}, "<=", 0));
        // restriction 2: at most three warehouses are open
        store.impose(new LinearInt(open, java.util.Arrays.copyOf(ones, nW), "<=", 3));
        // restriction 3: Atlanta or Los Angeles is open
        store.impose(new LinearInt(new IntVar[]{open[3], open[1]}, new int[]{1, 1}, ">=", 1));

        // total cost = sum fixed_costs[i] * open[i] + sum shipping_costs[i][j] * ships[i][j]
        int maxCost = 0;
        for (int i = 0; i < nW; i++)
            maxCost += fixedCosts.getInt(i);
        for (int j = 0; j < nR; j++) {
            int worst = 0;
            for (int i = 0; i < nW; i++)
                worst = Math.max(worst, shippingCosts.getJSONArray(i).getInt(j));
            maxCost += worst * demands.getInt(j);
        }
        IntVar total = new IntVar(store, 0, maxCost);

        int nTerms = nW + nW * nR + 1;
        IntVar[] terms = new IntVar[nTerms];
        int[] weights = new int[nTerms];
        int t = 0;
        for (int i = 0; i < nW; i++) {
            terms[t] = open[i];
            weights[t] = fixedCosts.getInt(i);
            t++;
        }
        for (int i = 0; i < nW; i++)
            for (int j = 0; j < nR; j++) {
                terms[t] = ships[i][j];
                weights[t] = shippingCosts.getJSONArray(i).getInt(j);
                t++;
            }
        // total is the last term, with weight -1, so that the sum equals zero
        terms[t] = total;
        weights[t] = -1;
        store.impose(new LinearInt(terms, weights, "==", 0));

        return new Model().put("open_warehouse", open).put("ships", ships)
                .put("total_cost", total).minimize(total);
    }
}
