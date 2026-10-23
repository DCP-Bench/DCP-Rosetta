// Costas arrays (CSPLib 076): a permutation X of 1..n such that all vectors between
// its marks are different. Written as the classic difference triangle: for each
// distance l = 1..n-1, the differences X[i] - X[i+l] must all be different.
// Output costas: the permutation X, 1-based, one value per position.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.XplusYeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");

        // X[i] is the value of the permutation at position i, in 1..n.
        IntVar[] x = new IntVar[n];
        for (int i = 0; i < n; i++) {
            x[i] = new IntVar(store, "x" + i, 1, n);
        }
        // A permutation: all values different.
        store.impose(new Alldifferent(x));

        // Difference triangle. Row l (distance l) holds X[i] - X[i+l] for each i.
        // Each row must not repeat a value, which is the Costas condition.
        for (int l = 1; l < n; l++) {
            int len = n - l;
            IntVar[] row = new IntVar[len];
            for (int i = 0; i < len; i++) {
                // diff = X[i] - X[i+l], written as X[i+l] + diff = X[i].
                IntVar diff = new IntVar(store, "d" + l + "_" + i, -(n - 1), n - 1);
                store.impose(new XplusYeqZ(x[i + l], diff, x[i]));
                row[i] = diff;
            }
            store.impose(new Alldifferent(row));
        }

        Model m = new Model().put("costas", x);
        m.search(x, null, null);   // label the permutation first, the differences follow
        return m;
    }
}
