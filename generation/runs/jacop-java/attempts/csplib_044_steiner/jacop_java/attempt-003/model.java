// Ternary Steiner system of order n: choose n*(n-1)/6 triples of elements from
// 1..n so that any two triples have at most one common element.
// sets[t][j] = true if element j is part of triple t.
import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject instance, Store store) {
        // The order n comes from the instance; the number of triples follows from it.
        int n = instance.getInt("n");
        int rows = n * (n - 1) / 6;

        // x[t][j] = 1 if element j (0-based) is part of triple t.
        BooleanVar[][] x = new BooleanVar[rows][n];
        IntVar[] decisions = new IntVar[rows * n];
        for (int t = 0; t < rows; t++) {
            for (int j = 0; j < n; j++) {
                x[t][j] = new BooleanVar(store, "x" + t + "_" + j);
                decisions[t * n + j] = x[t][j];
            }
        }

        // Each triple has exactly three elements.
        int[] ones = new int[n];
        java.util.Arrays.fill(ones, 1);
        for (int t = 0; t < rows; t++) {
            store.impose(new LinearInt(x[t], ones, "==", 3));
        }

        // Any two triples have at most one common element: for every pair of elements
        // (j, k), at most one triple contains both. p[t] = 1 exactly when triple t contains
        // both j and k, written as linear constraints on 0/1 variables.
        for (int j = 0; j < n; j++) {
            for (int k = j + 1; k < n; k++) {
                BooleanVar[] both = new BooleanVar[rows];
                int[] ones2 = new int[rows];
                java.util.Arrays.fill(ones2, 1);
                for (int t = 0; t < rows; t++) {
                    BooleanVar p = new BooleanVar(store, "both" + t + "_" + j + "_" + k);
                    both[t] = p;
                    // p <= x[t][j], p <= x[t][k], p >= x[t][j] + x[t][k] - 1
                    store.impose(new LinearInt(new IntVar[]{p, x[t][j]}, new int[]{1, -1}, "<=", 0));
                    store.impose(new LinearInt(new IntVar[]{p, x[t][k]}, new int[]{1, -1}, "<=", 0));
                    store.impose(new LinearInt(new IntVar[]{x[t][j], x[t][k], p}, new int[]{1, 1, -1}, "<=", 1));
                }
                // The pair {j, k} lies in at most one triple. Counting pairs (each triple
                // covers three, and there are n(n-1)/2 pairs) shows every pair is covered by
                // exactly one triple, so the bound is tightened to equality as an implied
                // constraint that gives stronger propagation.
                store.impose(new LinearInt(both, ones2, "==", 1));
            }
        }

        // Redundant (implied) constraint: each element j has n-1 other elements to pair
        // with, and each triple through j uses two of them, each pair used once. So every
        // element is in exactly (n-1)/2 triples. This is a consequence of the constraints
        // above, added to make propagation stronger.
        int degree = (n - 1) / 2;
        for (int j = 0; j < n; j++) {
            BooleanVar[] column = new BooleanVar[rows];
            for (int t = 0; t < rows; t++) {
                column[t] = x[t][j];
            }
            store.impose(new LinearInt(column, ones2(rows), "==", degree));
        }

        // Label the triple memberships first; the auxiliary pair variables follow from them.
        Model m = new Model().put("sets", x);
        m.search(decisions, null, null);
        return m;
    }

    private static int[] ones2(int size) {
        int[] ones = new int[size];
        java.util.Arrays.fill(ones, 1);
        return ones;
    }
}
