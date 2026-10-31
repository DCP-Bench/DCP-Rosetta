// Equal sized groups: divide a sorted list a of N elements into K contiguous groups by
// choosing K-1 break points x[1..K-1] (1-based: group g holds elements x[g-1]+1..x[g],
// with x[0] = 0 and x[K] = N). A break point may only fall where the value changes,
// because equal values must stay in one group. Each group's size should be close to
// round(N/K); the error of a group is |size - round(N/K)|. Minimise the total error.
// Output x: the K-1 break points, 1-based.
import org.jacop.constraints.AbsXeqY;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XltY;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray a = inst.getJSONArray("a");   // sorted values
        int n = a.length();                     // number of elements N
        int k = inst.getInt("k");               // number of groups K
        // round(N/K), with halves rounded to even as Python's round does.
        int target = (int) Math.rint((double) n / k);

        // xs[0] = 0 and xs[k] = N are fixed; xs[1..k-1] are the break points.
        IntVar[] xs = new IntVar[k + 1];
        xs[0] = new IntVar(store, "x0", 0, 0);
        xs[k] = new IntVar(store, "xK", n, n);
        for (int g = 1; g < k; g++) {
            xs[g] = new IntVar(store, "x" + g, 1, n - 1);
        }

        // A break point after element p (1-based) needs a[p] != a[p+1] (1-based), that is
        // a.getInt(p-1) != a.getInt(p) with the 0-based JSON array. Equal values stay together.
        int valid = 0;
        for (int p = 1; p < n; p++) {
            if (a.getInt(p - 1) != a.getInt(p)) {
                valid++;
            }
        }
        int[][] validPositions = new int[valid][1];
        int idx = 0;
        for (int p = 1; p < n; p++) {
            if (a.getInt(p - 1) != a.getInt(p)) {
                validPositions[idx++][0] = p;
            }
        }
        for (int g = 1; g < k; g++) {
            store.impose(new org.jacop.constraints.table.Table(
                new IntVar[]{xs[g]}, validPositions));
        }

        // Groups are non-empty and in order: 0 < x1 < ... < x(k-1) < N.
        for (int g = 0; g < k; g++) {
            store.impose(new XltY(xs[g], xs[g + 1]));
        }

        // Group g has size xs[g+1] - xs[g]. Its error is |size - target|.
        IntVar[] err = new IntVar[k];
        for (int g = 0; g < k; g++) {
            // dev = size - target, written as xs[g+1] - xs[g] - dev = target.
            IntVar dev = new IntVar(store, "dev" + g, -n, n);
            store.impose(new LinearInt(new IntVar[]{xs[g + 1], xs[g], dev},
                                       new int[]{1, -1, -1}, "==", target));
            err[g] = new IntVar(store, "err" + g, 0, n);
            store.impose(new AbsXeqY(dev, err[g]));
        }

        // Total error to minimise.
        IntVar total = new IntVar(store, "total", 0, k * n);
        store.impose(new SumInt(err, "==", total));

        IntVar[] breaks = new IntVar[k - 1];
        for (int g = 1; g < k; g++) {
            breaks[g - 1] = xs[g];
        }
        Model m = new Model().put("x", breaks);
        m.search(breaks, null, null);         // choose the break points first
        return m.minimize(total);
    }
}
