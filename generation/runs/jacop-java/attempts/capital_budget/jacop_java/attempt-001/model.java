import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

// Choose a subset of investments. x[i] is true when investment i is chosen.
// The total cash flow of the chosen investments must not exceed the budget.
// z is the total NPV of the chosen investments, and it is maximised.
public class Submission {
    public static Model build(JSONObject instance, Store store) {
        int budget = instance.getInt("budget");
        JSONArray cashFlowJson = instance.getJSONArray("cash_flow");
        JSONArray npvJson = instance.getJSONArray("npv");
        int n = cashFlowJson.length();

        int[] cashFlow = new int[n];
        int[] npv = new int[n];
        for (int i = 0; i < n; i++) {
            cashFlow[i] = cashFlowJson.getInt(i);
            npv[i] = npvJson.getInt(i);
        }

        BooleanVar[] x = new BooleanVar[n];
        for (int i = 0; i < n; i++) x[i] = new BooleanVar(store, "x" + i);

        // Budget: sum of cash_flow[i] * x[i] <= budget.
        store.impose(new LinearInt(x, cashFlow, "<=", budget));

        // NPV: z = sum of npv[i] * x[i]. Bounds come from the data: the smallest and largest
        // total that any subset can reach.
        int lo = 0, hi = 0;
        for (int i = 0; i < n; i++) {
            if (npv[i] < 0) lo += npv[i];
            else hi += npv[i];
        }
        IntVar z = new IntVar(store, lo, hi);
        IntVar[] terms = new IntVar[n + 1];
        int[] weights = new int[n + 1];
        for (int i = 0; i < n; i++) {
            terms[i] = x[i];
            weights[i] = npv[i];
        }
        terms[n] = z;
        weights[n] = -1;
        store.impose(new LinearInt(terms, weights, "==", 0));

        return new Model().put("x", x).put("z", z).maximize(z);
    }
}
