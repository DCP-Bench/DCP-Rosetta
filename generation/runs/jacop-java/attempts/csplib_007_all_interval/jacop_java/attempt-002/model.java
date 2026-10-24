// All-interval series of size n. x is a permutation of the pitch classes 0..n-1.
// The interval between neighbours, diffs[i] = |x[i+1] - x[i]|, is a permutation of
// 1..n-1, so every interval from a minor second to a major seventh occurs once.
import org.jacop.constraints.AbsXeqY;
import org.jacop.constraints.Alldistinct;
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.jacop.search.IndomainMin;
import org.jacop.search.SmallestDomain;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");

        // the series: each pitch class 0..n-1 occurs exactly once
        IntVar[] x = new IntVar[n];
        for (int i = 0; i < n; i++) {
            x[i] = new IntVar(store, "x" + i, 0, n - 1);
        }
        store.impose(new Alldistinct(x));

        // the intervals between neighbours: diffs[i] = |x[i+1] - x[i]|
        IntVar[] diffs = new IntVar[n - 1];
        for (int i = 0; i + 1 < n; i++) {
            // signed step d = x[i+1] - x[i], then its absolute value
            IntVar d = new IntVar(store, -(n - 1), n - 1);
            store.impose(new LinearInt(new IntVar[]{x[i + 1], x[i], d},
                    new int[]{1, -1, -1}, "==", 0));
            diffs[i] = new IntVar(store, 1, n - 1);
            store.impose(new AbsXeqY(d, diffs[i]));
        }

        // the n-1 intervals are all different, so they are 1..n-1 in some order
        store.impose(new Alldistinct(diffs));

        // label the intervals first: they are a permutation, so the search commits
        // to the interval sequence and the series follows by propagation
        return new Model().put("x", x).put("diffs", diffs)
                .search(diffs, new SmallestDomain<>(), new IndomainMin<>());
    }
}
