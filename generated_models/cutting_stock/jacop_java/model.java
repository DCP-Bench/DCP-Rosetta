// Cutting stock: raw rolls of width roll_width are cut into pieces of the given widths. The instance
// lists the cutting patterns (num_rolls_width[p][w] = pieces of width w cut from one roll with pattern p)
// and the number of pieces ordered of each width (orders[w]). Choose how many rolls to cut with each
// pattern so that, for every width, the pieces cut meet its order, and the total number of rolls is minimal.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.SumInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int numPatterns = inst.getInt("num_patterns");
        int numWidths = inst.getJSONArray("widths").length();
        JSONArray orders = inst.getJSONArray("orders");
        JSONArray patterns = inst.getJSONArray("num_rolls_width");

        // Total pieces ordered, over all widths. An optimal cutting never needs more rolls than this:
        // every roll it cuts has to supply at least one piece of an order.
        int totalOrders = 0;
        for (int w = 0; w < numWidths; w++) {
            totalOrders += orders.getInt(w);
        }

        // patternsUsed[p] = number of rolls cut with pattern p.
        IntVar[] patternsUsed = new IntVar[numPatterns];
        for (int p = 0; p < numPatterns; p++) {
            patternsUsed[p] = new IntVar(store, "pattern_" + p, 0, totalOrders);
        }

        // For each width, the pieces of that width cut over all rolls must meet its order.
        for (int w = 0; w < numWidths; w++) {
            int[] pieces = new int[numPatterns];
            for (int p = 0; p < numPatterns; p++) {
                pieces[p] = patterns.getJSONArray(p).getInt(w);
            }
            store.impose(new LinearInt(patternsUsed, pieces, ">=", orders.getInt(w)));
        }

        // The objective: the total number of raw rolls cut.
        IntVar minRolls = new IntVar(store, "min_rolls_cut", 0, totalOrders * numPatterns);
        store.impose(new SumInt(patternsUsed, "==", minRolls));

        // Label the pattern counts first; the total follows from them.
        return new Model()
                .put("min_rolls_cut", minRolls)
                .put("patterns_used", patternsUsed)
                .minimize(minRolls)
                .search(patternsUsed, null, null);
    }
}
