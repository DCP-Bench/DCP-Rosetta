// Best host: seat six guests around a round table so that as few neighbours as possible do not get
// along. Guests are numbered 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank. Output "x" lists
// the guest in each seat, in seating order around the table; seat 5 is next to seat 0.
// A conflict is an adjacent pair that do not get along. The get-along pairs form a six-cycle
// (Andrew-Dave-Erica-Betty-Cara-Frank-Andrew), so seating along that cycle gives zero conflicts.
// The model therefore requires every neighbouring pair to get along, which is the set of
// minimum-conflict arrangements, and it has no objective.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.table.Table;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;
import java.util.ArrayList;
import java.util.List;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = 6;

        // Guests who get along, as ordered pairs (both directions). Indices as in the output.
        // Andrew 0 with Dave 3 and Frank 5; Betty 1 with Cara 2 and Erica 4; Cara 2 with Frank 5;
        // Dave 3 with Erica 4.
        int[][] friends = {
            {0, 3}, {0, 5}, {1, 2}, {1, 4}, {2, 5}, {3, 4}
        };
        List<int[]> allowed = new ArrayList<>();
        for (int[] f : friends) {
            allowed.add(new int[]{f[0], f[1]});
            allowed.add(new int[]{f[1], f[0]});
        }
        int[][] tuples = allowed.toArray(new int[0][]);

        // Seat i holds guest x[i]; every guest sits in exactly one seat.
        IntVar[] x = new IntVar[n];
        for (int i = 0; i < n; i++) {
            x[i] = new IntVar(store, "seat_" + i, 0, n - 1);
        }
        store.impose(new Alldifferent(x));

        // Each pair of neighbours (seat i and the next seat, with seat 5 next to seat 0) gets along.
        for (int i = 0; i < n; i++) {
            IntVar[] pair = {x[i], x[(i + 1) % n]};
            store.impose(new Table(pair, tuples));
        }

        return new Model().put("x", x);
    }
}
