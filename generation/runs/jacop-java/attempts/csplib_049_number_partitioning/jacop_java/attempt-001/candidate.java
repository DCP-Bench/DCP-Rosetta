// Number partitioning: split the numbers 1..n into two sets A and B of equal size (n/2 each) with
// equal sums and equal sums of squares. Outputs "A" and "B" are arrays of n/2 values from 1..n.
// The instances have even n; each slot is one number, and all n slots together hold 1..n exactly once.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        int h = n / 2; // size of each set

        // Slots: a[k] is the k-th number of A and b[k] the k-th number of B.
        // The first h entries of all are A, the next h are B.
        IntVar[] a = new IntVar[h];
        IntVar[] b = new IntVar[h];
        IntVar[] all = new IntVar[n];
        for (int k = 0; k < h; k++) {
            a[k] = new IntVar(store, "A_" + k, 1, n);
            all[k] = a[k];
        }
        for (int k = 0; k < h; k++) {
            b[k] = new IntVar(store, "B_" + k, 1, n);
            all[h + k] = b[k];
        }

        // Every number 1..n appears exactly once across A and B (n slots, all different, domain 1..n).
        store.impose(new Alldifferent(all));

        // Equal sums: sum(A) - sum(B) = 0.
        IntVar[] sumVars = new IntVar[n];
        int[] sumWeights = new int[n];
        for (int i = 0; i < n; i++) {
            sumVars[i] = all[i];
            sumWeights[i] = i < h ? 1 : -1;
        }
        store.impose(new LinearInt(sumVars, sumWeights, "==", 0));

        // Equal sums of squares: sum(A squared) - sum(B squared) = 0.
        IntVar[] squares = new IntVar[n];
        for (int i = 0; i < n; i++) {
            squares[i] = new IntVar(store, 1, n * n);
            store.impose(new XmulYeqZ(all[i], all[i], squares[i]));
        }
        IntVar[] sqVars = new IntVar[n];
        int[] sqWeights = new int[n];
        for (int i = 0; i < n; i++) {
            sqVars[i] = squares[i];
            sqWeights[i] = i < h ? 1 : -1;
        }
        store.impose(new LinearInt(sqVars, sqWeights, "==", 0));

        // Decisions are the slots; label them before the squares.
        return new Model().put("A", a).put("B", b).search(all, null, null);
    }
}
