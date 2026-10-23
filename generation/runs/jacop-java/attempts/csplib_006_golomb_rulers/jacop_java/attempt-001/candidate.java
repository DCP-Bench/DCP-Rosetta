// Golomb ruler: m marks at integer positions 0 = a_1 < a_2 < ... < a_m such that
// all m(m-1)/2 pairwise differences a_j - a_i (i < j) are distinct. Minimise the
// length of the ruler, which is the position of the last mark a_m.
// marks[k] = position of mark k+1; length = marks[m-1].
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XltY;
import org.jacop.constraints.XplusYeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // number of marks, from the instance
        int m = inst.getInt("size");

        // the length is at most 2 m^2: a generous bound on the optimal length
        // (the optimum grows roughly like m^2); the marks lie within it
        int maxLen = 2 * m * m;

        IntVar[] marks = new IntVar[m];
        for (int k = 0; k < m; k++) {
            marks[k] = new IntVar(store, "a" + (k + 1), 0, maxLen);
        }
        // the first mark is at position 0
        store.impose(new XeqC(marks[0], 0));
        // marks are strictly increasing
        for (int k = 0; k + 1 < m; k++) {
            store.impose(new XltY(marks[k], marks[k + 1]));
        }

        // every difference a_j - a_i with i < j is a distinct value
        int pairs = m * (m - 1) / 2;
        IntVar[] diffs = new IntVar[pairs];
        int p = 0;
        for (int i = 0; i < m; i++) {
            for (int j = i + 1; j < m; j++) {
                // the difference is at least 1, since the marks are increasing
                IntVar d = new IntVar(store, 1, maxLen);
                // marks[j] = marks[i] + d
                store.impose(new XplusYeqZ(marks[i], d, marks[j]));
                diffs[p++] = d;
            }
        }
        store.impose(new Alldifferent(diffs));

        // the length is the position of the last mark, to be minimised
        Model model = new Model().put("marks", marks).put("length", marks[m - 1]);
        return model.minimize(marks[m - 1]);
    }
}
