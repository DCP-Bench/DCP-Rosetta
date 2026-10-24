// Aircraft landing on a single runway, with a fixed landing sequence.
// Each aircraft i lands at an integer time in [earliest_i, latest_i]. Landing
// earlier than target_i costs penalty_before_i per time unit; landing later costs
// penalty_after_i per time unit. For every pair i < j in the sequence, aircraft j
// lands at least separation_time[i][j] after aircraft i. Minimise the total penalty.
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray earliest = inst.getJSONArray("earliest_landing");
        JSONArray latest = inst.getJSONArray("latest_landing");
        JSONArray target = inst.getJSONArray("target_landing");
        JSONArray penAfter = inst.getJSONArray("penalty_after");
        JSONArray penBefore = inst.getJSONArray("penalty_before");
        JSONArray sep = inst.getJSONArray("separation_time");
        int n = earliest.length();

        // landing time of each aircraft, bounded by its time window
        IntVar[] land = new IntVar[n];
        for (int i = 0; i < n; i++) {
            land[i] = new IntVar(store, "t" + i,
                    earliest.getInt(i), latest.getInt(i));
        }

        // Penalty per aircraft: t_i - target_i = late_i - early_i, with late_i and
        // early_i the (non-negative) time after and before the target. The total
        // penalty is then sum(penalty_after * late_i + penalty_before * early_i).
        // Both can be positive only in a non-optimal point, so minimisation picks
        // the exact penalty.
        IntVar[] late = new IntVar[n];
        IntVar[] early = new IntVar[n];
        int totalMax = 0;
        for (int i = 0; i < n; i++) {
            int tgt = target.getInt(i);
            int lateMax = Math.max(0, latest.getInt(i) - tgt);
            int earlyMax = Math.max(0, tgt - earliest.getInt(i));
            late[i] = new IntVar(store, "late" + i, 0, lateMax);
            early[i] = new IntVar(store, "early" + i, 0, earlyMax);
            // t_i - late_i + early_i = target_i
            store.impose(new LinearInt(
                    new IntVar[]{land[i], late[i], early[i]},
                    new int[]{1, -1, 1}, "==", tgt));
            totalMax += penAfter.getInt(i) * lateMax + penBefore.getInt(i) * earlyMax;
        }

        // Separation between landings in the fixed sequence: for i < j,
        // t_j - t_i >= separation_time[i][j].
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                store.impose(new LinearInt(
                        new IntVar[]{land[j], land[i]},
                        new int[]{1, -1}, ">=", sep.getJSONArray(i).getInt(j)));
            }
        }

        // total penalty = sum over aircraft of the weighted early and late times
        IntVar total = new IntVar(store, "total_penalty", 0, totalMax);
        IntVar[] sumVars = new IntVar[2 * n + 1];
        int[] sumWeights = new int[2 * n + 1];
        for (int i = 0; i < n; i++) {
            sumVars[2 * i] = late[i];
            sumWeights[2 * i] = penAfter.getInt(i);
            sumVars[2 * i + 1] = early[i];
            sumWeights[2 * i + 1] = penBefore.getInt(i);
        }
        sumVars[2 * n] = total;
        sumWeights[2 * n] = -1;
        store.impose(new LinearInt(sumVars, sumWeights, "==", 0));

        Model m = new Model().put("landing_times", land).put("total_penalty", total);
        return m.minimize(total);
    }
}
