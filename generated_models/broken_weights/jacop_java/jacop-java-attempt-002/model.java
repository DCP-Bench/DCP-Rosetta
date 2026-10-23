// Broken weight. A weight of m pounds broke into n pieces, each a whole number of
// pounds. The pieces must weigh every integer from 1 to m on a balance scale: a
// piece is on the object's pan (+1), on the other pan (-1), or unused (0).
// Output the piece weights, in increasing order so each multiset appears once.
//
// Encoding: reach[j][x] is 1 when some signed choice of the first j pieces sums
// to value x - m (x in 0..2m). Adding piece j+1 with weight w keeps every reachable
// value and adds the values shifted by -w and +w. Each shifted lookup is an Element
// over a zero-padded copy of the previous row, so every value is decided by
// propagation rather than by searching over per-value choices. At the end every
// value 1..m must be reachable.
import org.jacop.constraints.Element;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Max;
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
        int[] ones = new int[n];
        java.util.Arrays.fill(ones, 1);
        store.impose(new LinearInt(w, ones, "==", m));

        // pieces in increasing order (strict, so no repeated weight)
        for (int j = 0; j + 1 < n; j++) {
            store.impose(new XltY(w[j], w[j + 1]));
        }

        IntVar zero = new IntVar(store, 0, 0);
        IntVar one = new IntVar(store, 1, 1);

        // reach[0]: with no pieces only the value 0 (index m) is reachable
        IntVar[] reach = new IntVar[2 * m + 1];
        for (int x = 0; x <= 2 * m; x++) {
            reach[x] = (x == m) ? one : zero;
        }

        for (int j = 0; j < n; j++) {
            // padded copy of the previous row: pad[k] = reach value k - 2m, or 0 if
            // that value lies outside -m..m, so every shifted index stays in range
            IntVar[] pad = new IntVar[4 * m + 1];
            for (int k = 0; k <= 4 * m; k++) {
                int x = k - 2 * m + m;
                pad[k] = (x >= 0 && x <= 2 * m) ? reach[x] : zero;
            }

            IntVar[] next = new IntVar[2 * m + 1];
            for (int x = 0; x <= 2 * m; x++) {
                // lookup of value (x - m) - w_j, index x + m - w_j
                IntVar iMinus = new IntVar(store, 0, 4 * m);
                store.impose(new LinearInt(new IntVar[]{iMinus, w[j]},
                        new int[]{1, 1}, "==", x + m));
                IntVar fromMinus = new IntVar(store, 0, 1);
                store.impose(Element.choose(iMinus, pad, fromMinus, -1));

                // lookup of value (x - m) + w_j, index x + m + w_j
                IntVar iPlus = new IntVar(store, 0, 4 * m);
                store.impose(new LinearInt(new IntVar[]{iPlus, w[j]},
                        new int[]{1, -1}, "==", x + m));
                IntVar fromPlus = new IntVar(store, 0, 1);
                store.impose(Element.choose(iPlus, pad, fromPlus, -1));

                // the value is reachable with j+1 pieces if it was reachable with j
                // pieces, or with one more piece on either pan
                next[x] = new IntVar(store, 0, 1);
                store.impose(new Max(new IntVar[]{reach[x], fromMinus, fromPlus}, next[x]));
            }
            reach = next;
        }

        // every weight 1..m is reachable
        for (int v = 1; v <= m; v++) {
            store.impose(new org.jacop.constraints.XeqC(reach[m + v], 1));
        }

        // labelling the pieces first keeps the search on the answer, not the lookups
        return new Model().put("weights", w).search(w, null, null);
    }
}
