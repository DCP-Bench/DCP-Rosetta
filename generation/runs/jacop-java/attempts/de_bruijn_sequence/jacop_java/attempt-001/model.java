// de Bruijn sequence B(base, n) (de Bruijn sequence): a cyclic sequence of length
// base^n over the symbols 0..base-1 in which every length-n string occurs exactly once
// as a cyclic substring. Output de_bruijn: the sequence itself.
// The cyclic windows of length n are encoded as integers in base-base positional
// notation and must all be different.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int base = inst.getInt("base");       // alphabet size k
        int n = inst.getInt("n");             // order: window length
        int len = 1;                          // sequence length k^n
        for (int i = 0; i < n; i++) {
            len *= base;
        }

        IntVar[] seq = new IntVar[len];
        for (int i = 0; i < len; i++) {
            seq[i] = new IntVar(store, "s" + i, 0, base - 1);
        }

        // The window value of the cyclic window starting at position i:
        // sum over j of seq[(i+j) mod len] * base^(n-1-j), in 0..base^n-1.
        IntVar[] window = new IntVar[len];
        for (int i = 0; i < len; i++) {
            IntVar[] vars = new IntVar[n + 1];
            int[] weights = new int[n + 1];
            int power = 1;
            for (int j = n - 1; j >= 0; j--) {
                // The last position in the window has weight 1, the first base^(n-1).
                vars[j] = seq[(i + j) % len];
                weights[j] = power;
                power *= base;
            }
            window[i] = new IntVar(store, "w" + i, 0, len - 1);
            // window[i] is the value of the window: sum of weights * symbols - window = 0.
            vars[n] = window[i];
            weights[n] = -1;
            store.impose(new LinearInt(vars, weights, "==", 0));
        }

        // Every length-n string occurs once, so all window values are different.
        store.impose(new Alldifferent(window));

        Model m = new Model().put("de_bruijn", seq);
        m.search(seq, null, null);            // label the sequence, the windows follow
        return m;
    }
}
