// Assignment costs: assign each of the tasks to exactly one person, minimising the total cost.
// Not every person has to get a task, but each person takes at most one task.
// cost[i][j] = cost of task i done by person j; x[i][j] = 1 means task i is assigned to person j.
// Objective: the total cost of the chosen (task, person) pairs, to be minimised.

import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray cost = inst.getJSONArray("cost");
        int tasks = cost.length();                     // number of tasks, from the instance
        int people = cost.getJSONArray(0).length();    // number of people, from the instance

        // x[i][j]: task i is assigned to person j
        BooleanVar[][] x = new BooleanVar[tasks][people];
        for (int i = 0; i < tasks; i++) {
            for (int j = 0; j < people; j++) {
                x[i][j] = new BooleanVar(store, "x" + i + "_" + j);
            }
        }

        int[] ones = new int[people];
        for (int j = 0; j < people; j++) ones[j] = 1;
        int[] onesT = new int[tasks];
        for (int i = 0; i < tasks; i++) onesT[i] = 1;

        // each task is assigned to exactly one person
        for (int i = 0; i < tasks; i++) {
            store.impose(new LinearInt(x[i], ones, "==", 1));
        }

        // each person takes at most one task
        for (int j = 0; j < people; j++) {
            BooleanVar[] column = new BooleanVar[tasks];
            for (int i = 0; i < tasks; i++) column[i] = x[i][j];
            store.impose(new LinearInt(column, onesT, "<=", 1));
        }

        // total = sum of cost[i][j] * x[i][j].
        // Each task contributes exactly one cost, so the total lies between the sum of the row
        // minima and the sum of the row maxima. Those bounds come from the instance.
        long lo = 0, hi = 0;
        for (int i = 0; i < tasks; i++) {
            JSONArray row = cost.getJSONArray(i);
            int rowMin = Integer.MAX_VALUE, rowMax = Integer.MIN_VALUE;
            for (int j = 0; j < people; j++) {
                rowMin = Math.min(rowMin, row.getInt(j));
                rowMax = Math.max(rowMax, row.getInt(j));
            }
            lo += rowMin;
            hi += rowMax;
        }
        IntVar total = new IntVar(store, "total", (int) lo, (int) hi);

        // one linear equation: sum of cost * x - total = 0
        int terms = tasks * people + 1;
        BooleanVar[] vars = new BooleanVar[terms];
        int[] weights = new int[terms];
        int k = 0;
        for (int i = 0; i < tasks; i++) {
            JSONArray row = cost.getJSONArray(i);
            for (int j = 0; j < people; j++) {
                vars[k] = x[i][j];
                weights[k] = row.getInt(j);
                k++;
            }
        }
        // the last term is total itself, with weight -1; it is an IntVar, so vars is IntVar[]
        IntVar[] allVars = new IntVar[terms];
        for (int t = 0; t < terms - 1; t++) allVars[t] = vars[t];
        allVars[terms - 1] = total;
        weights[terms - 1] = -1;
        store.impose(new LinearInt(allVars, weights, "==", 0));

        Model model = new Model().put("x", x);
        return model.minimize(total);
    }
}
