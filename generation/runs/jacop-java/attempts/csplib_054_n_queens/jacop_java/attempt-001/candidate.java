// N-queens (CSPLib 054): place n queens on an n x n board so that no two share
// a row, a column or a diagonal.
//
// Variables: queens[i] in 1..n is the column of the queen in row i (1-based,
// as the output convention requires). Each row holds exactly one queen by
// construction: the position in the array is the row.
//
// Constraints, in the problem's own terms:
//   - no two queens share a column: the queens are all different;
//   - no two queens share a "/" diagonal: up[i] = queens[i] + i are all different;
//   - no two queens share a "\" diagonal: down[i] = queens[i] - i are all different.
//     The shifts by i turn each diagonal into a single value, so all-different
//     over them forbids two queens on one diagonal.
//
// Sizes come from the instance: n. Nothing here depends on the example.

import org.jacop.constraints.Alldistinct;
import org.jacop.constraints.XplusCeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");

        IntVar[] queens = new IntVar[n];
        IntVar[] up = new IntVar[n];     // queens[i] + i
        IntVar[] down = new IntVar[n];   // queens[i] - i
        for (int i = 0; i < n; i++) {
            queens[i] = new IntVar(store, "q_" + i, 1, n);
            up[i] = new IntVar(store, "up_" + i, 1 + i, n + i);
            down[i] = new IntVar(store, "down_" + i, 1 - i, n - i);
        }
        for (int i = 0; i < n; i++) {
            store.impose(new XplusCeqZ(queens[i], i, up[i]));     // up = queens + i
            store.impose(new XplusCeqZ(down[i], i, queens[i]));   // down + i = queens
        }

        store.impose(new Alldistinct(queens));
        store.impose(new Alldistinct(up));
        store.impose(new Alldistinct(down));

        Model m = new Model().put("queens", queens);
        return m;
    }
}
