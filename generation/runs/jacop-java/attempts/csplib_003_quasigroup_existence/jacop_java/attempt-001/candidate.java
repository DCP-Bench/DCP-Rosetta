// QG3.m quasigroup existence: find an order-m Latin square q (every symbol 0..m-1 appears
// exactly once in each row and each column) such that (a*b)*(b*a) = a for all a, b.
// Output "quasigroup" is q[row][col], values 0..m-1. Only m is read from the instance.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.Element;
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int m = inst.getInt("m");

        // Cell variables: q[i][j] is the product i*j. flat[i*m+j] is the same variable, so that
        // Element can index the whole table with a single integer index.
        IntVar[][] q = new IntVar[m][m];
        IntVar[] flat = new IntVar[m * m];
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < m; j++) {
                q[i][j] = new IntVar(store, "q_" + i + "_" + j, 0, m - 1);
                flat[i * m + j] = q[i][j];
            }
        }

        // Latin square: each row and each column is a permutation of 0..m-1.
        for (int i = 0; i < m; i++) {
            store.impose(new Alldifferent(q[i]));
        }
        for (int j = 0; j < m; j++) {
            IntVar[] column = new IntVar[m];
            for (int i = 0; i < m; i++) {
                column[i] = q[i][j];
            }
            store.impose(new Alldifferent(column));
        }

        // (a*b)*(b*a) = a for every pair a, b. Here ab = q[a][b] and ba = q[b][a], and the outer
        // product is q[ab][ba] = flat[ab*m + ba], which must equal the constant a.
        for (int a = 0; a < m; a++) {
            for (int b = 0; b < m; b++) {
                IntVar ab = q[a][b];
                IntVar ba = q[b][a];

                // idx = ab*m + ba, the position of (a*b)*(b*a) in flat.
                // If a == b, ab and ba are the same variable, so the weights are merged.
                IntVar idx = new IntVar(store, "idx_" + a + "_" + b, 0, m * m - 1);
                if (a == b) {
                    store.impose(new LinearInt(new IntVar[]{ab, idx}, new int[]{m + 1, -1}, "==", 0));
                } else {
                    store.impose(new LinearInt(new IntVar[]{ab, ba, idx}, new int[]{m, 1, -1}, "==", 0));
                }

                // flat[idx] == a, the required value of (a*b)*(b*a).
                IntVar aConst = new IntVar(store, a, a);
                store.impose(Element.choose(idx, flat, aConst, -1));
            }
        }

        // Decision variables (the table) first, so the search labels them before the helpers.
        return new Model().put("quasigroup", q).search(flat, null, null);
    }
}
