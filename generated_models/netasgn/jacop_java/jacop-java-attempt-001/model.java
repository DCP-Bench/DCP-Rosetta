// Project assignment (transportation problem): assign hours from each person to each project so that
// every person's supply is used up, every project's demand is met exactly, no person-project pair exceeds
// its limit, and the total cost of the hours is minimised.
import org.jacop.constraints.*;
import org.jacop.core.*;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray supplyJson = inst.getJSONArray("supply");
        JSONArray demandJson = inst.getJSONArray("demand");
        JSONArray costJson = inst.getJSONArray("cost");
        JSONArray limitJson = inst.getJSONArray("limit");
        int people = supplyJson.length();
        int projects = demandJson.length();

        // assign[i][j]: hours from person i to project j, between 0 and the limit for that pair.
        IntVar[][] assign = new IntVar[people][projects];
        IntVar[] flat = new IntVar[people * projects];
        int[] flatCost = new int[people * projects];
        int maxCost = 0;
        for (int i = 0; i < people; i++) {
            for (int j = 0; j < projects; j++) {
                int limit = limitJson.getJSONArray(i).getInt(j);
                assign[i][j] = new IntVar(store, "assign" + i + "_" + j, 0, limit);
                flat[i * projects + j] = assign[i][j];
                flatCost[i * projects + j] = costJson.getJSONArray(i).getInt(j);
                maxCost += flatCost[i * projects + j] * limit;
            }
        }

        // Each person's hours sum to their supply.
        for (int i = 0; i < people; i++) {
            IntVar[] row = new IntVar[projects];
            int[] ones = new int[projects];
            for (int j = 0; j < projects; j++) {
                row[j] = assign[i][j];
                ones[j] = 1;
            }
            store.impose(new LinearInt(row, ones, "==", supplyJson.getInt(i)));
        }

        // Each project's hours sum to its demand.
        for (int j = 0; j < projects; j++) {
            IntVar[] column = new IntVar[people];
            int[] ones = new int[people];
            for (int i = 0; i < people; i++) {
                column[i] = assign[i][j];
                ones[i] = 1;
            }
            store.impose(new LinearInt(column, ones, "==", demandJson.getInt(j)));
        }

        // total_cost = sum of cost[i][j] * assign[i][j]: written as sum - total_cost = 0.
        IntVar totalCost = new IntVar(store, 0, maxCost);
        IntVar[] costVars = new IntVar[flat.length + 1];
        int[] costWeights = new int[flat.length + 1];
        for (int k = 0; k < flat.length; k++) {
            costVars[k] = flat[k];
            costWeights[k] = flatCost[k];
        }
        costVars[flat.length] = totalCost;
        costWeights[flat.length] = -1;
        store.impose(new LinearInt(costVars, costWeights, "==", 0));

        Model m = new Model().put("assign", assign).put("total_cost", totalCost);
        m.search(flat, null, null);
        return m.minimize(totalCost);
    }
}
