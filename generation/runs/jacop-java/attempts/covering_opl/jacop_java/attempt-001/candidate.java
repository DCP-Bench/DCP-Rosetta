// Set covering with hiring costs: choose a set of workers so that every task is
// performed by at least one hired worker who is qualified for it, at the lowest
// total hiring cost.

import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Instance data: Qualified[t] lists (1-based) the workers qualified for
        // task t, Cost[i] is the hiring cost of worker i. The rows of Qualified
        // have different lengths, so each is read on its own.
        int workers = inst.getInt("nb_workers");
        int tasks = inst.getInt("num_tasks");
        JSONArray costJson = inst.getJSONArray("Cost");
        JSONArray qualified = inst.getJSONArray("Qualified");

        int[] cost = new int[workers];
        int costSum = 0;
        for (int i = 0; i < workers; i++) {
            cost[i] = costJson.getInt(i);
            costSum += cost[i];
        }

        // hired[i] = 1 if worker i is hired (the declared output, 0-based index i).
        BooleanVar[] hired = new BooleanVar[workers];
        for (int i = 0; i < workers; i++) {
            hired[i] = new BooleanVar(store, "hired_" + i);
        }
        IntVar[] hiredVars = hired;

        // Every task is performed: at least one qualified worker for it is hired.
        for (int t = 0; t < tasks; t++) {
            JSONArray row = qualified.getJSONArray(t);
            IntVar[] candidates = new IntVar[row.length()];
            int[] ones = new int[row.length()];
            for (int k = 0; k < row.length(); k++) {
                candidates[k] = hired[row.getInt(k) - 1];
                ones[k] = 1;
            }
            store.impose(new LinearInt(candidates, ones, ">=", 1));
        }

        // Objective: total = sum of Cost[i] * hired[i].
        IntVar total = new IntVar(store, "total_cost", 0, costSum);
        IntVar[] costVars = new IntVar[workers + 1];
        int[] costWeights = new int[workers + 1];
        for (int i = 0; i < workers; i++) {
            costVars[i] = hired[i];
            costWeights[i] = cost[i];
        }
        costVars[workers] = total;
        costWeights[workers] = -1;
        store.impose(new LinearInt(costVars, costWeights, "==", 0));

        // Labels the hiring decisions first; the cost total follows.
        return new Model()
                .put("total_cost", total)
                .put("workers", hired)
                .search(hiredVars, null, null)
                .minimize(total);
    }
}
