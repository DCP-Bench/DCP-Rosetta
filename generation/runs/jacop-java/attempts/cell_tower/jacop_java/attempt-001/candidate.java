// Cell tower coverage: choose which candidate sites get a cell tower so that the
// total build cost stays within the budget and the population covered by the
// built towers is as large as possible.

import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XeqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Instance data: delta[i][r] = 1 if a tower at site i covers region r,
        // cost[i] the cost of site i, population[r] the people in region r,
        // budget the total cost allowed.
        JSONArray delta = inst.getJSONArray("delta");
        JSONArray costJson = inst.getJSONArray("cost");
        JSONArray popJson = inst.getJSONArray("population");
        int budget = inst.getInt("budget");

        int sites = costJson.length();
        int regions = popJson.length();

        int[] cost = new int[sites];
        for (int i = 0; i < sites; i++) {
            cost[i] = costJson.getInt(i);
        }
        int[] population = new int[regions];
        int totalPopulation = 0;
        for (int r = 0; r < regions; r++) {
            population[r] = popJson.getInt(r);
            totalPopulation += population[r];
        }

        // build[i] = 1 if a tower is built at site i (the decision output).
        BooleanVar[] build = new BooleanVar[sites];
        for (int i = 0; i < sites; i++) {
            build[i] = new BooleanVar(store, "build_" + i);
        }
        IntVar[] buildVars = build;

        // covered[r] = 1 if region r has at least one tower in range.
        BooleanVar[] covered = new BooleanVar[regions];
        for (int r = 0; r < regions; r++) {
            covered[r] = new BooleanVar(store, "covered_" + r);
        }

        // A region can only count as covered when a built tower reaches it:
        // covered[r] <= sum of build[i] over the sites i that cover r.
        // A region no site reaches is never covered.
        for (int r = 0; r < regions; r++) {
            int count = 0;
            for (int i = 0; i < sites; i++) {
                if (delta.getJSONArray(i).getInt(r) == 1) {
                    count++;
                }
            }
            if (count == 0) {
                store.impose(new XeqC(covered[r], 0));
                continue;
            }
            IntVar[] vars = new IntVar[count + 1];
            int[] weights = new int[count + 1];
            int k = 0;
            for (int i = 0; i < sites; i++) {
                if (delta.getJSONArray(i).getInt(r) == 1) {
                    vars[k] = build[i];
                    weights[k] = 1;
                    k++;
                }
            }
            vars[count] = covered[r];
            weights[count] = -1;
            store.impose(new LinearInt(vars, weights, ">=", 0));
        }

        // Budget: the total cost of the built towers is at most the budget.
        store.impose(new LinearInt(buildVars, cost, "<=", budget));

        // Objective: total = sum over regions of population[r] * covered[r].
        IntVar total = new IntVar(store, "total_population_covered", 0, totalPopulation);
        IntVar[] totalVars = new IntVar[regions + 1];
        int[] totalWeights = new int[regions + 1];
        for (int r = 0; r < regions; r++) {
            totalVars[r] = covered[r];
            totalWeights[r] = population[r];
        }
        totalVars[regions] = total;
        totalWeights[regions] = -1;
        store.impose(new LinearInt(totalVars, totalWeights, "==", 0));

        // Labels the tower decisions first; the coverage variables follow.
        return new Model()
                .put("build_tower", build)
                .put("total_population_covered", total)
                .search(buildVars, null, null)
                .maximize(total);
    }
}
