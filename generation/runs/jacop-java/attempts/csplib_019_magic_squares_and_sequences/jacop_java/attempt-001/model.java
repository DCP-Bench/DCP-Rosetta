// Magic sequence of length n: x[0..n-1], each x[i] between 0 and n-1, such that the
// value i occurs exactly x[i] times in the sequence.
// Sizes come from the instance field n.
import org.jacop.constraints.Count;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XeqY;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {

    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");

        // x[i] is the number of occurrences of value i, so it lies in 0..n-1.
        IntVar[] x = new IntVar[n];
        for (int i = 0; i < n; i++)
            x[i] = new IntVar(store, "x_" + i, 0, n - 1);

        // "the number i occurs exactly x[i] times": count the occurrences of value i in the
        // sequence into a fresh counter, and tie that counter to x[i].
        for (int i = 0; i < n; i++) {
            IntVar occurrences = new IntVar(store, "occurrences_" + i, 0, n);
            store.impose(new Count(x, occurrences, i));
            store.impose(new XeqY(occurrences, x[i]));
        }

        // Every position holds one value, so the counts add up to n. This is implied by the
        // constraints above; it is posted to help propagation.
        store.impose(new SumInt(x, "==", new IntVar(store, n, n)));

        return new Model().put("x", x);
    }
}
