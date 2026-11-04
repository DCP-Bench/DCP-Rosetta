// Added corners: place the digits 1 to 8, each once, in the four circles (corners of a
// 3x3 frame) and the four squares (midpoints of its sides). Each square holds the sum of
// the two circles next to it.
// Outputs: "positions", the 8 cells in reading order (left to right, top to bottom):
//   0 = top-left circle,     1 = top square,     2 = top-right circle,
//   3 = left square,         4 = right square,
//   5 = bottom-left circle,  6 = bottom square,  7 = bottom-right circle.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.XplusYeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // The problem fixes the layout and the digits, so this model has no instance data.
        IntVar[] p = new IntVar[8];
        for (int i = 0; i < 8; i++) {
            p[i] = new IntVar(store, "p" + i, 1, 8);
        }
        IntVar tl = p[0], topSq = p[1], tr = p[2];
        IntVar leftSq = p[3], rightSq = p[4];
        IntVar bl = p[5], bottomSq = p[6], br = p[7];

        // Every digit 1 to 8 is used exactly once, over circles and squares alike.
        store.impose(new Alldifferent(p));

        // Top square = top-left circle + top-right circle.
        store.impose(new XplusYeqZ(tl, tr, topSq));
        // Left square = top-left circle + bottom-left circle.
        store.impose(new XplusYeqZ(tl, bl, leftSq));
        // Right square = top-right circle + bottom-right circle.
        store.impose(new XplusYeqZ(tr, br, rightSq));
        // Bottom square = bottom-left circle + bottom-right circle.
        store.impose(new XplusYeqZ(bl, br, bottomSq));

        return new Model().put("positions", p);
    }
}
