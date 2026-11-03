// Frog circle: n cards 1..n are placed on a circle of n positions (0..n-1, clockwise).
// From its current card k the frog jumps k places clockwise, starting on card 1.
// Find an arrangement x (x[p] = card at position p) from which the frog lands on every card.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.Circuit;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XgteqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // The circle size n comes from the instance; every array below is sized from it.
        int n = inst.getInt("n");

        // x[p] = card at position p, a card number from 1 to n, each card used once.
        IntVar[] x = new IntVar[n];
        for (int p = 0; p < n; p++) {
            x[p] = new IntVar(store, "x" + p, 1, n);
        }
        store.impose(new Alldifferent(x));

        // Successor of each position: the frog on position p jumps x[p] places clockwise,
        // to position (p + x[p]) mod n. nxt[p] holds that position in 1-based form, because
        // the Circuit constraint works on 1-based values.
        // With p in 0-based form, p + x[p] lies in p+1 .. p+n. It wraps past n-1 exactly when
        // x[p] >= n - p, which is recorded in wrap[p]. Wrapping subtracts n.
        // So nxt[p] = (p + x[p] - n * wrap[p]) + 1, written as a linear equation.
        IntVar[] nxt = new IntVar[n];
        for (int p = 0; p < n; p++) {
            nxt[p] = new IntVar(store, "nxt" + p, 1, n);
            BooleanVar wrap = new BooleanVar(store, "wrap" + p);
            // wrap[p] <-> the jump from position p goes past the end of the circle
            store.impose(new Reified(new XgteqC(x[p], n - p), wrap));
            // nxt[p] = x[p] + p + 1 - n * wrap[p]
            store.impose(new LinearInt(new IntVar[]{nxt[p], x[p], wrap},
                                       new int[]{1, -1, n}, "==", p + 1));
        }

        // The frog must visit every position before returning, so the successor
        // function is one single cycle over all n positions. Circuit enforces that.
        // It also rules out a jump that lands back on its own position.
        store.impose(new Circuit(nxt));

        // Output: the arrangement x. No ordering or fixing of card 1 is added, since the
        // description does not ask for one. Labelling x first fixes nxt and wrap as well.
        Model m = new Model().put("x", x);
        return m.search(x, null, null);
    }
}
