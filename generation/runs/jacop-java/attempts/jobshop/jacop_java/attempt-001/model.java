// Job shop: several jobs, each a fixed sequence of tasks; each task runs on one given machine
// for a given duration. Tasks of a job run in order, a machine runs one task at a time, and a
// started task runs to completion. Minimise the makespan (the time all jobs finish).
// Each job's data is a list of [machine, duration] pairs; jobs may have different task counts.
import org.jacop.constraints.Or;
import org.jacop.constraints.XplusClteqZ;
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

        // A machine processes one task at a time. For any two tasks on the same machine, one of
        // them ends before the other starts.
        for (int j1 = 0; j1 < nJobs; j1++) {
            for (int t1 = 0; t1 < machine[j1].length; t1++) {
                for (int j2 = j1; j2 < nJobs; j2++) {
                    for (int t2 = (j2 == j1 ? t1 + 1 : 0); t2 < machine[j2].length; t2++) {
                        if (machine[j1][t1] != machine[j2][t2]) {
                            continue;
                        }
                        store.impose(new Or(
                            new XplusClteqZ(start[j1][t1], duration[j1][t1], start[j2][t2]),
                            new XplusClteqZ(start[j2][t2], duration[j2][t2], start[j1][t1])));
                    }
                }
            }
        }

        // The makespan is at least the end of every job's last task.
        IntVar makespan = new IntVar(store, "makespan", 0, horizon);
        for (int j = 0; j < nJobs; j++) {
            int last = machine[j].length - 1;
            store.impose(new XplusClteqZ(start[j][last], duration[j][last], makespan));
        }

        // Output: the makespan, minimised. Labelling the start times fixes the schedule.
        IntVar[] allStarts = new IntVar[countTasks(machine)];
        int k = 0;
        for (int j = 0; j < nJobs; j++) {
            for (int t = 0; t < machine[j].length; t++) {
                allStarts[k++] = start[j][t];
            }
        }
        Model m = new Model().put("makespan", makespan).search(allStarts, null, null);
        return m.minimize(makespan);
    }

    private static int countTasks(int[][] machine) {
        int total = 0;
        for (int[] job : machine) {
            total += job.length;
        }
        return total;
    }
}
