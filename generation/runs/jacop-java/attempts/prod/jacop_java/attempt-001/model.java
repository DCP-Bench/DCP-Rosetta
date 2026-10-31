// Product mix: choose production quantities X[j] of each product j, 0 <= X[j] <= u[j].
// Resource: sum of X[j] / a[j] must not exceed the budget b (a time limit).
// Profit: sum of c[j] * X[j]; maximise it.
// JaCoP works on integers, so the time constraint is multiplied through by L = lcm(a[j]):
// sum (L / a[j]) * X[j] <= b * L, which is the same constraint with integer weights.
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    private static long gcd(long x, long y) {
        return y == 0 ? x : gcd(y, x % y);
    }

    public static Model build(JSONObject inst, Store store) {
        JSONArray a = inst.getJSONArray("a");   // time per unit, per product
        JSONArray c = inst.getJSONArray("c");   // profit per unit, per product
        JSONArray u = inst.getJSONArray("u");   // upper bound on each production quantity
        int b = inst.getInt("b");               // time budget
        int n = a.length();

        // L = lcm of the a[j]: the common denominator of the time constraint
        long L = 1;
        for (int j = 0; j < n; j++) {
            long aj = a.getInt(j);
            L = L / gcd(L, aj) * aj;
        }

        // X[j] = production quantity of product j
        IntVar[] X = new IntVar[n];
        for (int j = 0; j < n; j++)
            X[j] = new IntVar(store, "X" + j, 0, u.getInt(j));

        // Time constraint: sum (L/a[j]) * X[j] <= b * L
        int[] timeW = new int[n];
        for (int j = 0; j < n; j++)
            timeW[j] = (int) (L / a.getInt(j));
        store.impose(new LinearInt(X, timeW, "<=", (int) (b * L)));

        // Total profit = sum c[j] * X[j], with its largest possible value as the upper bound
        int maxProfit = 0;
        for (int j = 0; j < n; j++)
            maxProfit += c.getInt(j) * u.getInt(j);
        IntVar total = new IntVar(store, 0, maxProfit);
        int[] profitW = new int[n + 1];
        IntVar[] terms = new IntVar[n + 1];
        for (int j = 0; j < n; j++) {
            terms[j] = X[j];
            profitW[j] = c.getInt(j);
        }
        // total - sum c[j] * X[j] = 0
        terms[n] = total;
        profitW[n] = -1;
        store.impose(new LinearInt(terms, profitW, "==", 0));

        return new Model().put("x", X).put("total_profit", total).maximize(total);
    }
}
