// Hadamard matrix Legendre pairs (CSPLib 084): find two sequences A, B of l values
// in {-1, +1} whose periodic autocorrelations add up to -2 at every shift s = 1..m,
// with m = (l-1)/2, and whose sums are both 1.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.constraints.XneqC;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int l = inst.getInt("l");     // sequence length, from the instance
        int m = (l - 1) / 2;          // number of shifts s = 1..m

        // a[i], b[i] take the values -1 or +1: domain [-1, 1] without 0
        IntVar[] a = new IntVar[l];
        IntVar[] b = new IntVar[l];
        for (int i = 0; i < l; i++) {
            a[i] = new IntVar(store, -1, 1);
            store.impose(new XneqC(a[i], 0));
            b[i] = new IntVar(store, -1, 1);
            store.impose(new XneqC(b[i], 0));
        }

        int[] ones = new int[l];
        java.util.Arrays.fill(ones, 1);
        // linear constraints: the sum of A is 1 and the sum of B is 1
        store.impose(new LinearInt(a, ones, "==", 1));
        store.impose(new LinearInt(b, ones, "==", 1));

        // periodic autocorrelation: for each shift s, PAF(A, s) + PAF(B, s) = -2,
        // where PAF(X, s) = sum_i x_i * x_{(i + s) mod l}.
        IntVar minusTwo = new IntVar(store, -2, -2);
        for (int s = 1; s <= m; s++) {
            IntVar[] products = new IntVar[2 * l];
            for (int i = 0; i < l; i++) {
                int j = (i + s) % l;
                // product terms of PAF(A, s) and PAF(B, s)
                products[i] = new IntVar(store, -1, 1);
                store.impose(new XmulYeqZ(a[i], a[j], products[i]));
                products[l + i] = new IntVar(store, -1, 1);
                store.impose(new XmulYeqZ(b[i], b[j], products[l + i]));
            }
            store.impose(new SumInt(products, "==", minusTwo));
        }

        return new Model().put("a", a).put("b", b);
    }
}
