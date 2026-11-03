// Multi-commodity transportation: ship every product from origins to destinations so that
// each destination gets its demand of each product, no origin ships more of a product
// than its supply, and the total units on each origin-destination lane (all products
// together) stay within the lane limit. Minimise the total shipping cost.
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray supply = inst.getJSONArray("supply");   // [origin][product]
        JSONArray demand = inst.getJSONArray("demand");   // [destination][product]
        JSONArray limit = inst.getJSONArray("limit");     // [origin][destination]
        JSONArray cost = inst.getJSONArray("cost");       // [origin][destination][product]
        int nO = supply.length();
        int nD = demand.length();
        int nP = supply.getJSONArray(0).length();

        // x[i][j][p] = units of product p shipped from origin i to destination j
        IntVar[][][] x = new IntVar[nO][nD][nP];
        for (int i = 0; i < nO; i++)
            for (int j = 0; j < nD; j++)
                for (int p = 0; p < nP; p++) {
                    int ub = Math.min(supply.getJSONArray(i).getInt(p),
                            Math.min(demand.getJSONArray(j).getInt(p), limit.getJSONArray(i).getInt(j)));
                    x[i][j][p] = new IntVar(store, 0, Math.max(0, ub));
                }

        int[] ones = new int[Math.max(nO, nD)];
        java.util.Arrays.fill(ones, 1);

        // supply: the units of product p leaving origin i do not exceed its supply
        for (int i = 0; i < nO; i++)
            for (int p = 0; p < nP; p++) {
                IntVar[] out = new IntVar[nD];
                for (int j = 0; j < nD; j++)
                    out[j] = x[i][j][p];
                store.impose(new LinearInt(out, java.util.Arrays.copyOf(ones, nD), "<=",
                        supply.getJSONArray(i).getInt(p)));
            }

        // demand: each destination receives exactly its demand of each product
        for (int j = 0; j < nD; j++)
            for (int p = 0; p < nP; p++) {
                IntVar[] in = new IntVar[nO];
                for (int i = 0; i < nO; i++)
                    in[i] = x[i][j][p];
                store.impose(new LinearInt(in, java.util.Arrays.copyOf(ones, nO), "==",
                        demand.getJSONArray(j).getInt(p)));
            }

        // lane limit: all products together on the lane from origin i to destination j
        for (int i = 0; i < nO; i++)
            for (int j = 0; j < nD; j++) {
                IntVar[] lane = new IntVar[nP];
                for (int p = 0; p < nP; p++)
                    lane[p] = x[i][j][p];
                store.impose(new LinearInt(lane, java.util.Arrays.copyOf(ones, nP), "<=",
                        limit.getJSONArray(i).getInt(j)));
            }

        // total shipping cost, as an integer objective. It is split by demand: for each
        // destination j and product p, C[j][p] is the cost of the units delivered there.
        // Each such unit costs at least the cheapest origin's rate, so C[j][p] is bounded
        // below by demand * that rate; this bound lets the objective prune early.
        IntVar[][] C = new IntVar[nD][nP];
        IntVar total = null;
        int maxCost = 0;
        for (int j = 0; j < nD; j++)
            for (int p = 0; p < nP; p++) {
                int d = demand.getJSONArray(j).getInt(p);
                int minRate = Integer.MAX_VALUE;
                int maxRate = 0;
                IntVar[] vars = new IntVar[nO + 1];
                int[] w = new int[nO + 1];
                for (int i = 0; i < nO; i++) {
                    int c = cost.getJSONArray(i).getJSONArray(j).getInt(p);
                    minRate = Math.min(minRate, c);
                    maxRate = Math.max(maxRate, c);
                    vars[i] = x[i][j][p];
                    w[i] = c;
                }
                int cap = maxRate * d;
                maxCost += cap;
                C[j][p] = new IntVar(store, 0, cap);
                // sum_i cost[i][j][p] * x[i][j][p] = C[j][p]
                vars[nO] = C[j][p];
                w[nO] = -1;
                store.impose(new LinearInt(vars, w, "==", 0));
                // every unit of demand costs at least the cheapest rate
                store.impose(new LinearInt(new IntVar[]{C[j][p]}, new int[]{1}, ">=", minRate * d));
            }

        total = new IntVar(store, 0, maxCost);
        int nC = nD * nP;
        IntVar[] terms = new IntVar[nC + 1];
        int[] weights = new int[nC + 1];
        int t = 0;
        for (int j = 0; j < nD; j++)
            for (int p = 0; p < nP; p++) {
                terms[t] = C[j][p];
                weights[t] = 1;
                t++;
            }
        // total is the last term, with weight -1, so that the sum equals zero
        terms[nC] = total;
        weights[nC] = -1;
        store.impose(new LinearInt(terms, weights, "==", 0));

        return new Model().put("total_cost", total).minimize(total);
    }
}
