// Media selection: choose a set of advertising media so that every target audience is
// reached by at least one chosen medium, at the lowest total cost.
import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray costs = inst.getJSONArray("media_costs");          // one per medium
        JSONArray incidence = inst.getJSONArray("incidence_matrix"); // [audience][medium]
        int nMedia = costs.length();
        int nAudience = inst.getJSONArray("target_audiences").length();

        // is_selected[m] = 1 if medium m is bought
        BooleanVar[] selected = new BooleanVar[nMedia];
        for (int m = 0; m < nMedia; m++)
            selected[m] = new BooleanVar(store, "selected_" + m);

        // coverage: each audience is reached by at least one selected medium that covers it
        for (int a = 0; a < nAudience; a++) {
            JSONArray row = incidence.getJSONArray(a);
            java.util.List<BooleanVar> covering = new java.util.ArrayList<>();
            for (int m = 0; m < nMedia; m++)
                if (row.getInt(m) != 0)
                    covering.add(selected[m]);
            if (covering.isEmpty())
                continue; // no medium reaches this audience: nothing to post
            BooleanVar[] vars = covering.toArray(new BooleanVar[0]);
            int[] ones = new int[vars.length];
            java.util.Arrays.fill(ones, 1);
            store.impose(new LinearInt(vars, ones, ">=", 1));
        }

        // total cost = sum of media_costs[m] * selected[m], as an integer objective
        int maxCost = 0;
        for (int m = 0; m < nMedia; m++)
            maxCost += costs.getInt(m);
        IntVar total = new IntVar(store, 0, maxCost);
        IntVar[] terms = new IntVar[nMedia + 1];
        int[] weights = new int[nMedia + 1];
        for (int m = 0; m < nMedia; m++) {
            terms[m] = selected[m];
            weights[m] = costs.getInt(m);
        }
        // total is the last term, with weight -1, so that the weighted sum equals zero
        terms[nMedia] = total;
        weights[nMedia] = -1;
        store.impose(new LinearInt(terms, weights, "==", 0));

        return new Model().put("is_selected", selected).put("min_total_cost", total).minimize(total);
    }
}
