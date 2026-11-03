// Job shop: several jobs, each a fixed sequence of tasks; each task runs on one given machine
// for a given duration. Tasks of a job run in order, a machine runs one task at a time, and a
// started task runs to completion. Minimise the makespan (the time all jobs finish).
// Each job's data is a list of [machine, duration] pairs; jobs may have different task counts.
import java.util.ArrayList;
import java.util.List;
import org.jacop.constraints.XplusClteqZ;
import org.jacop.constraints.cumulative.CumulativeUnary;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Jobs, their tasks, machines and durations all come from the instance.
        JSONArray jobs = inst.getJSONArray("jobs_data");
        int nJobs = jobs.length();

        // Horizon: the sum of all durations bounds every start time and the makespan.
        int horizon = 0;
        int[][] machine = new int[nJobs][];
        int[][] duration = new int[nJobs][];
        for (int j = 0; j < nJobs; j++) {
            JSONArray job = jobs.getJSONArray(j);
            machine[j] = new int[job.length()];
            duration[j] = new int[job.length()];
            for (int t = 0; t < job.length(); t++) {
                JSONArray task = job.getJSONArray(t);
                machine[j][t] = task.getInt(0);
                duration[j][t] = task.getInt(1);
                horizon += duration[j][t];
            }
        }

        // start[j][t] = the time task t of job j starts.
        IntVar[][] start = new IntVar[nJobs][];
        for (int j = 0; j < nJobs; j++) {
            start[j] = new IntVar[machine[j].length];
            for (int t = 0; t < machine[j].length; t++) {
                start[j][t] = new IntVar(store, "start" + j + "_" + t, 0, horizon);
            }
        }

        // Tasks of a job run in their order: a task starts after the previous one has ended.
        for (int j = 0; j < nJobs; j++) {
            for (int t = 0; t + 1 < machine[j].length; t++) {
                store.impose(new XplusClteqZ(start[j][t], duration[j][t], start[j][t + 1]));
            }
        }

        // A machine processes one task at a time: a unary cumulative resource per machine.
        // Each task uses one unit of its machine, and the machine has capacity one.
        int maxMachine = 0;
        for (int[] mch : machine) {
            for (int id : mch) {
                maxMachine = Math.max(maxMachine, id);
            }
        }
        for (int mc = 0; mc <= maxMachine; mc++) {
            List<IntVar> s = new ArrayList<>();
            List<IntVar> d = new ArrayList<>();
            List<IntVar> r = new ArrayList<>();
            for (int j = 0; j < nJobs; j++) {
                for (int t = 0; t < machine[j].length; t++) {
                    if (machine[j][t] == mc) {
                        s.add(start[j][t]);
                        d.add(new IntVar(store, duration[j][t], duration[j][t]));
                        r.add(new IntVar(store, 1, 1));
                    }
                }
            }
            if (s.size() > 1) {
                store.impose(new CumulativeUnary(s.toArray(new IntVar[0]),
                                                 d.toArray(new IntVar[0]),
                                                 r.toArray(new IntVar[0]),
                                                 new IntVar(store, 1, 1)));
            }
        }

        // The makespan is at least the end of every job's last task.
        IntVar makespan = new IntVar(store, "makespan", 0, horizon);
        for (int j = 0; j < nJobs; j++) {
            int last = machine[j].length - 1;
            store.impose(new XplusClteqZ(start[j][last], duration[j][last], makespan));
        }

        // Output: the makespan, minimised. Labelling the start times fixes the schedule.
        List<IntVar> allStarts = new ArrayList<>();
        for (int j = 0; j < nJobs; j++) {
            for (int t = 0; t < machine[j].length; t++) {
                allStarts.add(start[j][t]);
            }
        }
        Model m = new Model().put("makespan", makespan)
                             .search(allStarts.toArray(new IntVar[0]), null, null);
        return m.minimize(makespan);
    }
}
