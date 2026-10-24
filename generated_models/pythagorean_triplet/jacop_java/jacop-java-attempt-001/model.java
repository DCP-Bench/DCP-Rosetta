// Pythagorean triplet: natural numbers a < b < c with a^2 + b^2 = c^2 and a + b + c = 1000.
// Output: a, b, c of that triplet.

import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XltY;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.constraints.XplusYeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Problem constant: the perimeter of the triangle is 1000.
        int perimeter = 1000;
        // Each side is at least 1 and, with the other two positive, at most perimeter - 3.
        // The problem says there is one triplet with a + b + c = 1000; a < b < c picks that
        // triplet's ordering, so the sides are distinct and a is the smallest.
        int maxSide = perimeter - 3;
        // Upper bound for a square: maxSide^2 = 994009.
        int maxSquare = maxSide * maxSide;

        IntVar a = new IntVar(store, "a", 1, maxSide);
        IntVar b = new IntVar(store, "b", 1, maxSide);
        IntVar c = new IntVar(store, "c", 1, maxSide);

        // a < b < c.
        store.impose(new XltY(a, b));
        store.impose(new XltY(b, c));

        // a + b + c = 1000.
        store.impose(new LinearInt(new IntVar[]{a, b, c}, new int[]{1, 1, 1}, "==", perimeter));

        // a^2 + b^2 = c^2.
        IntVar aSquare = new IntVar(store, "aSquare", 1, maxSquare);
        IntVar bSquare = new IntVar(store, "bSquare", 1, maxSquare);
        IntVar cSquare = new IntVar(store, "cSquare", 1, maxSquare);
        store.impose(new XmulYeqZ(a, a, aSquare));
        store.impose(new XmulYeqZ(b, b, bSquare));
        store.impose(new XmulYeqZ(c, c, cSquare));
        store.impose(new XplusYeqZ(aSquare, bSquare, cSquare));

        return new Model().put("a", a).put("b", b).put("c", c);
    }
}
