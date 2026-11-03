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

        // total shipping cost, as an integer objective
        int nTerms = nO * nD * nP;
        IntVar[] terms = new IntVar[nTerms + 1];
        int[] weights = new int[nTerms + 1];
        int maxCost = 0;
        int t = 0;
        for (int i = 0; i < nO; i++)
            for (int j = 0; j < nD; j++)
                for (int p = 0; p < nP; p++) {
                    terms[t] = x[i][j][p];
                    weights[t] = cost.getJSONArray(i).getJSONArray(j).getInt(p);
                    maxCost += weights[t] * x[i][j][p].max();
                    t++;
                }
        IntVar total = new IntVar(store, 0, maxCost);
        // total is the last term, with weight -1, so that the weighted sum equals zero
        terms[nTerms] = total;
        weights[nTerms] = -1;
        store.impose(new LinearInt(terms, weights, "==", 0));

        return new Model().put("total_cost", total).minimize(total);
    }
}
