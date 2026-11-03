// Broken weight. A weight of m pounds broke into n pieces, each a whole number of
// pounds. The pieces must weigh every integer from 1 to m on a balance scale: a
// piece is on the object's pan (+1), on the other pan (-1), or unused (0).
// Output the piece weights, in increasing order so each multiset appears once.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.constraints.XltY;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        int m = inst.getInt("m");

        // piece weights: whole pounds, each between 1 and the total m
        IntVar[] w = new IntVar[n];
        for (int j = 0; j < n; j++) {
            w[j] = new IntVar(store, "w" + j, 1, m);
        }

        // the pieces add up to the whole weight
        store.impose(new LinearInt(w, ones(n), "==", m));

        // pieces are listed in increasing order (strict, so no repeated weight)
        for (int j = 0; j + 1 < n; j++) {
            store.impose(new XltY(w[j], w[j + 1]));
        }

        // every weight v in 1..m is a signed sum of pieces: each piece is on the
        // object's pan (+1), on the other pan (-1) or unused (0). c[v][j] holds
        // that choice and t[v][j] = c[v][j] * w[j] its signed weight.
        for (int v = 1; v <= m; v++) {
            IntVar[] t = new IntVar[n];
            for (int j = 0; j < n; j++) {
                IntVar c = new IntVar(store, "c" + v + "_" + j, -1, 1);
                t[j] = new IntVar(store, "t" + v + "_" + j, -m, m);
                store.impose(new XmulYeqZ(c, w[j], t[j]));
            }
            store.impose(new LinearInt(t, ones(n), "==", v));
        }

        return new Model().put("weights", w);
    }

    private static int[] ones(int n) {
        int[] a = new int[n];
        java.util.Arrays.fill(a, 1);
        return a;
    }
}
