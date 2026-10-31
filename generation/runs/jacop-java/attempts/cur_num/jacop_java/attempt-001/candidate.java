// Find a number p between 1 and 10000, other than 48, such that p + 1 is a square and
// half of p plus 1 is also a square. (p must be even so that its half is a whole number.)
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.constraints.XneqC;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject instance, Store store) {
        // The number p and its half h = p / 2.
        IntVar p = new IntVar(store, 1, 10000);
        IntVar h = new IntVar(store, 0, 5000);
        // p is even, so p = 2 * h and the half is a whole number.
        store.impose(new LinearInt(new IntVar[]{p, h}, new int[]{1, -2}, "==", 0));
        // "Another number": the example 48 is excluded.
        store.impose(new XneqC(p, 48));

        // p + 1 is a square: p + 1 = s * s.
        IntVar s = new IntVar(store, 1, 101);
        IntVar pPlusOne = new IntVar(store, 2, 10001);
        store.impose(new XmulYeqZ(s, s, pPlusOne));
        store.impose(new LinearInt(new IntVar[]{pPlusOne, p}, new int[]{1, -1}, "==", 1));

        // half of p plus 1 is a square: h + 1 = t * t.
        IntVar t = new IntVar(store, 1, 71);
        IntVar hPlusOne = new IntVar(store, 1, 5001);
        store.impose(new XmulYeqZ(t, t, hPlusOne));
        store.impose(new LinearInt(new IntVar[]{hPlusOne, h}, new int[]{1, -1}, "==", 1));

        Model m = new Model().put("peculiar", p);
        m.search(new IntVar[]{p}, null, null);
        return m;
    }
}
