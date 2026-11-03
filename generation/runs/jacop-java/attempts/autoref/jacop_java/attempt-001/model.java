// Auto-referential series. Given n and m, find a series S = (s_0, ..., s_{n+1})
// such that s_i is the number of occurrences of the value i in S, for every
// i in 0..n, and s_{n+1} = m. The output s has n+2 entries.
import org.jacop.constraints.Count;
import org.jacop.constraints.XeqC;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        int m = inst.getInt("m");
        int len = n + 2;

        // each entry of S is a count, bounded here by the largest value the series
        // can name, n+1; the series has n+2 entries (indices 0..n+1)
        IntVar[] s = new IntVar[len];
        for (int i = 0; i < len; i++) {
            s[i] = new IntVar(store, "s" + i, 0, n + 1);
        }

        // s_{n+1} = m
        store.impose(new XeqC(s[n + 1], m));

        // for each i in 0..n: the number of entries of S equal to i is s_i
        for (int i = 0; i <= n; i++) {
            store.impose(new Count(s, s[i], i));
        }

        return new Model().put("s", s);
    }
}
