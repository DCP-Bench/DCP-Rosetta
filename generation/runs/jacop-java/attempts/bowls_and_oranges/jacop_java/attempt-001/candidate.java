// Bowls and oranges: n bowls in a line at 1 metre intervals (bowls numbered 1..n), and
// m oranges, one per bowl, such that no three oranges A, B, C have dist(A,B) == dist(B,C).
// x[k] is the bowl of the k-th orange, in ascending order.
// n and m come from the instance fields n and m.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XltY;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {

    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        int m = inst.getInt("m");

        // x[k]: the bowl holding orange k, one of 1..n.
        IntVar[] x = new IntVar[m];
        for (int k = 0; k < m; k++)
            x[k] = new IntVar(store, "x_" + k, 1, n);

        // The output is listed in ascending order, and "one orange per bowl" means the bowls
        // are all different; a strictly increasing list gives both.
        for (int k = 0; k + 1 < m; k++)
            store.impose(new XltY(x[k], x[k + 1]));

        // No three oranges in arithmetic progression. Because the list is sorted, the three
        // oranges i < j < k have B = x[j] in the middle, so the forbidden case is
        // dist(A,B) == dist(B,C), i.e. x[i] + x[k] == 2 * x[j].
        for (int i = 0; i < m; i++) {
            for (int j = i + 1; j < m; j++) {
                for (int k = j + 1; k < m; k++) {
                    store.impose(new LinearInt(new IntVar[]{x[i], x[k], x[j]},
                                               new int[]{1, 1, -2}, "!=", 0));
                }
            }
        }

        return new Model().put("x", x);
    }
}
