// Twelve-pack problem: buy some packs of each size so that the number of items
// meets or exceeds the target, and the total number of items is as close to the
// target as possible (the total is minimised).
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject instance, Store store) {
        // The pack sizes and the target come from the instance; the number of pack sizes follows the data.
        JSONArray packsJson = instance.getJSONArray("packs");
        int n = packsJson.length();
        int target = instance.getInt("target");
        int[] packs = new int[n];
        int minPack = Integer.MAX_VALUE;
        for (int i = 0; i < n; i++) {
            packs[i] = packsJson.getInt(i);
            minPack = Math.min(minPack, packs[i]);
        }

        // Bound on the total: adding copies of the smallest pack to reach the target
        // gives a total in [target, target + minPack - 1], so the optimum lies there.
        int maxTotal = target + minPack - 1;

        // counts[i] = number of packs of size packs[i] bought.
        IntVar[] counts = new IntVar[n];
        for (int i = 0; i < n; i++) {
            counts[i] = new IntVar(store, "count" + i, 0, maxTotal / packs[i]);
        }

        // total = number of items bought, at least the target.
        IntVar total = new IntVar(store, "total", target, maxTotal);

        // total = sum over sizes of packs[i] * counts[i]
        // (encoded as sum packs[i] * counts[i] - total = 0).
        IntVar[] terms = new IntVar[n + 1];
        int[] weights = new int[n + 1];
        for (int i = 0; i < n; i++) {
            terms[i] = counts[i];
            weights[i] = packs[i];
        }
        terms[n] = total;
        weights[n] = -1;
        store.impose(new LinearInt(terms, weights, "==", 0));

        // Decision variables are the pack counts; total is fixed by them.
        Model m = new Model().put("counts", counts);
        m.search(counts, null, null);
        // Minimise the total number of items, i.e. the closest combination that meets the target.
        return m.minimize(total);
    }
}
