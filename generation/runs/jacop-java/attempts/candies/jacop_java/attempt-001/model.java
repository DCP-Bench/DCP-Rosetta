// Candies: children sit in a line with rating scores. Every child gets at least
// one candy, and of two neighbours the child with the higher rating gets more
// candies than the other. Minimise the total number of candies (z).
// x[i] = candies for child i; z = total candies.
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XltY;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // number of children, and their ratings (from the instance, not the example)
        JSONArray ratings = inst.getJSONArray("ratings");
        int n = ratings.length();

        // each child gets between 1 and n candies: a strictly decreasing run of
        // n children needs at most n candies, so n bounds every x[i]
        IntVar[] x = new IntVar[n];
        for (int i = 0; i < n; i++) {
            x[i] = new IntVar(store, "x" + i, 1, n);
        }

        // total number of candies, between one each and the largest possible sum
        IntVar z = new IntVar(store, "z", n, n * n);
        // the total is the sum of all children's candies
        store.impose(new SumInt(x, "==", z));

        // neighbours: the child with the higher rating must get more candies
        // than the one with the lower rating; equal ratings impose nothing
        for (int i = 0; i + 1 < n; i++) {
            int ri = ratings.getInt(i);
            int rj = ratings.getInt(i + 1);
            if (ri > rj) {
                // x[i+1] < x[i]
                store.impose(new XltY(x[i + 1], x[i]));
            } else if (ri < rj) {
                // x[i] < x[i+1]
                store.impose(new XltY(x[i], x[i + 1]));
            }
        }

        // output the per-child candies and the total, minimise the total
        Model m = new Model().put("x", x).put("z", z);
        return m.minimize(z);
    }
}
