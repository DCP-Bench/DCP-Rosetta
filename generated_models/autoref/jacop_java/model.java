// Auto-referential series. Given n and m, find a series S = (s_0, ..., s_{n+1})
// such that s_i is the number of occurrences of the value i in S, for every
// i in 0..n, and s_{n+1} = m. The output s has n+2 entries.
import org.jacop.constraints.GCC;
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

        // each entry of S is a count of a value in 0..n, so it lies in 0..n
        IntVar[] s = new IntVar[len];
        for (int i = 0; i < len; i++) {
            s[i] = new IntVar(store, "s" + i, 0, n);
        }

        // s_{n+1} = m
        store.impose(new XeqC(s[n + 1], m));

        // GCC counts the values 0, 1, ... in order: counters[i] is the number of
        // entries of s equal to i. The counters are the first n+1 entries of s, so
        // s_i = number of occurrences of i. (Count with a counter that is also in
        // the counted list is unsound in JaCoP, so GCC is used instead.)
        IntVar[] counters = new IntVar[n + 1];
        for (int i = 0; i <= n; i++) {
            counters[i] = s[i];
        }
        store.impose(new GCC(s, counters));

        return new Model().put("s", s);
    }
}
