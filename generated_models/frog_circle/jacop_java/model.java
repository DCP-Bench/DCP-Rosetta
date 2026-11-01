// Frog circle: n cards 1..n sit on n positions 0..n-1 of a circle, clockwise.
// The frog starts on card 1 at position 0 and from card k jumps k places clockwise, forever.
// Find an arrangement x (x[p] = card at position p) from which the frog lands on every card.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.Element;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Or;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XplusCeqZ;
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

        // x[p] = card at position p: each card 1..n appears once.
        IntVar[] x = new IntVar[n];
        for (int p = 0; p < n; p++) {
            x[p] = new IntVar(store, "x" + p, 1, n);
        }
        store.impose(new Alldifferent(x));

        // The frog starts on card 1, which sits at position 0 (the arrangement is read from there).
        store.impose(new XeqC(x[0], 1));

        // time[p] = the step at which the frog lands on position p. The frog lands on every
        // position exactly once, so the times are a permutation of 0..n-1, with time 0 at position 0.
        IntVar[] time = new IntVar[n];
        for (int p = 0; p < n; p++) {
            time[p] = new IntVar(store, "time" + p, 0, n - 1);
        }
        store.impose(new Alldifferent(time));
        store.impose(new XeqC(time[0], 0));

        // Landing position of a jump from p: next[p] = (p + x[p]) mod n, in 0-based form.
        // The jump wraps past the end of the circle exactly when x[p] >= n - p; wrap[p] records it.
        // So next[p] = p + x[p] - n * wrap[p].
        IntVar[] next = new IntVar[n];
        for (int p = 0; p < n; p++) {
            next[p] = new IntVar(store, "next" + p, 0, n - 1);
            BooleanVar wrap = new BooleanVar(store, "wrap" + p);
            store.impose(new Reified(new XgteqC(x[p], n - p), wrap));
            // next[p] = p + x[p] - n * wrap[p]
            store.impose(new LinearInt(new IntVar[]{next[p], x[p], wrap},
                                       new int[]{1, -1, n}, "==", p));
        }

        // Path condition: a position that is not the last one visited is followed by the next
        // step in time. So if time[p] < n-1, then time[next[p]] = time[p] + 1.
        // The landing time is looked up with Element, indexed by next[p] (0-based).
        for (int p = 0; p < n; p++) {
            IntVar afterTime = new IntVar(store, "afterTime" + p, 0, n - 1);
            store.impose(Element.choose(next[p], time, afterTime, -1));
            // Either this is the last position (time n-1), or the landing time is one more.
            store.impose(new Or(new XeqC(time[p], n - 1),
                                new XplusCeqZ(time[p], 1, afterTime)));
        }

        // Output: the arrangement x. Labelling x first fixes the rest.
        Model m = new Model().put("x", x);
        return m.search(x, null, null);
    }
}
