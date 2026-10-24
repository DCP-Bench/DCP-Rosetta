// Giant cat army: build a list of 24 integers, starting at 0 and ending at 14, where each step adds 5,
// adds 7, or takes the square root (only when that is an integer). All elements are distinct, at most 60,
// and the list contains 2, then 10, then 14 in that order (other numbers may lie between them).
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.table.Table;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {

    static final int LENGTH = 24;   // the list has 24 elements
    static final int MAX = 60;      // every element is at most 60

    public static Model build(JSONObject instance, Store store) {
        IntVar[] x = new IntVar[LENGTH];
        for (int i = 0; i < LENGTH; i++) {
            x[i] = new IntVar(store, "x" + i, 0, MAX);
        }
        // The list starts at 0 and ends at 14.
        store.impose(new XeqC(x[0], 0));
        store.impose(new XeqC(x[LENGTH - 1], 14));

        // One step: (previous, next) is allowed when next = previous + 5, next = previous + 7,
        // or next is the square root of previous (previous is a perfect square).
        int count = 0;
        for (int v = 0; v <= MAX; v++) {
            for (int w = 0; w <= MAX; w++) {
                if (w == v + 5 || w == v + 7 || w * w == v) {
                    count++;
                }
            }
        }
        int[][] steps = new int[count][];
        int k = 0;
        for (int v = 0; v <= MAX; v++) {
            for (int w = 0; w <= MAX; w++) {
                if (w == v + 5 || w == v + 7 || w * w == v) {
                    steps[k++] = new int[]{v, w};
                }
            }
        }
        for (int i = 0; i + 1 < LENGTH; i++) {
            store.impose(new Table(new IntVar[]{x[i], x[i + 1]}, steps));
        }

        // All elements are distinct.
        store.impose(new Alldifferent(x));

        // in2[i] = 1 when x[i] = 2, in10[i] = 1 when x[i] = 10.
        BooleanVar[] in2 = new BooleanVar[LENGTH];
        BooleanVar[] in10 = new BooleanVar[LENGTH];
        for (int i = 0; i < LENGTH; i++) {
            in2[i] = new BooleanVar(store, "in2_" + i);
            in10[i] = new BooleanVar(store, "in10_" + i);
            store.impose(new Reified(new XeqC(x[i], 2), in2[i]));
            store.impose(new Reified(new XeqC(x[i], 10), in10[i]));
        }

        // The list contains 2 and 10.
        IntVar[] present2 = new IntVar[LENGTH];
        int[] ones = new int[LENGTH];
        for (int i = 0; i < LENGTH; i++) {
            present2[i] = in2[i];
            ones[i] = 1;
        }
        store.impose(new LinearInt(present2, ones, ">=", 1));
        IntVar[] present10 = new IntVar[LENGTH];
        for (int i = 0; i < LENGTH; i++) {
            present10[i] = in10[i];
        }
        store.impose(new LinearInt(present10, ones, ">=", 1));

        // 2 comes before 10: every 10 at position i needs a 2 at some position before i.
        for (int i = 1; i < LENGTH; i++) {
            IntVar[] vars = new IntVar[i + 1];
            int[] weights = new int[i + 1];
            for (int j = 0; j < i; j++) {
                vars[j] = in2[j];
                weights[j] = 1;
            }
            vars[i] = in10[i];
            weights[i] = -1;
            store.impose(new LinearInt(vars, weights, ">=", 0));
        }

        Model model = new Model().put("x", x);
        return model;
    }
}
