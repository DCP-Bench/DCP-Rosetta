// Resource-constrained project scheduling: n jobs with durations and per-resource needs.
// A job starts only after its predecessors finish (successor links), and at any time the jobs
// running together must not use more than each resource's capacity. Minimise the makespan,
// which is the start of the final (sink) job, since it has no duration.
import java.util.ArrayList;
import java.util.List;
import org.jacop.constraints.XplusClteqZ;
import org.jacop.constraints.cumulative.Cumulative;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Job count, durations, needs, capacities and links all come from the instance.
        JSONArray durationsData = inst.getJSONArray("durations_data");
        JSONArray needsData = inst.getJSONArray("resource_needs_data");
        JSONArray capacitiesData = inst.getJSONArray("resource_capacities_data");
        JSONArray linksData = inst.getJSONArray("successors_link_data");
        int n = durationsData.length();
        int resources = capacitiesData.length();

        // The horizon is the sum of all durations: no job needs to start later than that.
        int horizon = 0;
        int[] duration = new int[n];
        for (int j = 0; j < n; j++) {
            duration[j] = durationsData.getInt(j);
            horizon += duration[j];
        }

        // start[j] = the time job j starts. Times start at 0.
        IntVar[] start = new IntVar[n];
        for (int j = 0; j < n; j++) {
            start[j] = new IntVar(store, "start" + j, 0, horizon);
        }

        // Precedence: a job starts only after its predecessor has finished.
        // Each link [a, b] says that job a must end before job b starts.
        for (int k = 0; k < linksData.length(); k++) {
            int a = linksData.getJSONArray(k).getInt(0);
            int b = linksData.getJSONArray(k).getInt(1);
            store.impose(new XplusClteqZ(start[a], duration[a], start[b]));
        }

        // Resources: at every time the sum of needs of running jobs stays within capacity.
        // One cumulative constraint per resource, with the job durations and that resource's needs.
        // The cumulative constraint needs durations above zero, so the zero-duration source and
        // sink jobs are left out of it; they use no resource.
        List<Integer> active = new ArrayList<>();
        for (int j = 0; j < n; j++) {
            if (duration[j] > 0) {
                active.add(j);
            }
        }
        IntVar[] actStart = new IntVar[active.size()];
        IntVar[] actDur = new IntVar[active.size()];
        for (int a = 0; a < active.size(); a++) {
            int j = active.get(a);
            actStart[a] = start[j];
            actDur[a] = new IntVar(store, duration[j], duration[j]);
        }
        // Likewise a job that needs none of a resource is left out of that resource's constraint.
        for (int r = 0; r < resources; r++) {
            List<IntVar> sVars = new ArrayList<>();
            List<IntVar> dVars = new ArrayList<>();
            List<IntVar> needVars = new ArrayList<>();
            for (int a = 0; a < active.size(); a++) {
                int j = active.get(a);
                int used = needsData.getJSONArray(j).getInt(r);
                if (used > 0) {
                    sVars.add(actStart[a]);
                    dVars.add(actDur[a]);
                    needVars.add(new IntVar(store, used, used));
                }
            }
            int capacity = capacitiesData.getInt(r);
            if (sVars.size() > 0) {
                store.impose(new Cumulative(sVars.toArray(new IntVar[0]),
                                            dVars.toArray(new IntVar[0]),
                                            needVars.toArray(new IntVar[0]),
                                            new IntVar(store, capacity, capacity)));
            }
        }

        // The makespan is the start of the last job, which is the sink with no duration.
        // Output: the start times, minimised through the makespan.
        IntVar makespan = start[n - 1];
        Model m = new Model().put("start_time", start).search(start, null, null);
        return m.minimize(makespan);
    }
}
