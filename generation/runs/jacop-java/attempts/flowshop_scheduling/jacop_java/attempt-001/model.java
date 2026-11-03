// Permutation flowshop: all jobs go through machines 1..M in the same order.
// Decide the job sequence; minimise the makespan (completion time of the last job on the last machine).
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.Element;
import org.jacop.constraints.Max;
import org.jacop.constraints.XplusYeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray pt = inst.getJSONArray("process_time");   // pt[job][machine], 0-based
        int n = pt.length();                                  // number of jobs
        int M = pt.getJSONArray(0).length();                  // number of machines

        int[][] p = new int[n][M];
        int sumAll = 0;
        for (int j = 0; j < n; j++)
            for (int m = 0; m < M; m++) {
                p[j][m] = pt.getJSONArray(j).getInt(m);
                sumAll += p[j][m];
            }

        // seq[k] = job in position k of the sequence (0-based job index)
        IntVar[] seq = new IntVar[n];
        for (int k = 0; k < n; k++)
            seq[k] = new IntVar(store, "seq" + k, 0, n - 1);
        // every job appears exactly once in the sequence
        store.impose(new Alldifferent(seq));

        // column m of the processing times, indexed by job, for Element
        int[][] col = new int[M][n];
        for (int m = 0; m < M; m++)
            for (int j = 0; j < n; j++)
                col[m][j] = p[j][m];

        // ptk[k][m] = processing time of the job in position k on machine m
        // C[k][m]   = completion time of position k on machine m
        IntVar[][] ptk = new IntVar[n][M];
        IntVar[][] C = new IntVar[n][M];
        for (int k = 0; k < n; k++)
            for (int m = 0; m < M; m++) {
                int lo = 0, hi = 0;
                for (int j = 0; j < n; j++) {
                    lo = (j == 0) ? p[j][m] : Math.min(lo, p[j][m]);
                    hi = Math.max(hi, p[j][m]);
                }
                ptk[k][m] = new IntVar(store, "pt" + k + "_" + m, lo, hi);
                // Element.choose is 0-based here (offset -1): pt = col[m][seq[k]]
                store.impose(Element.choose(seq[k], col[m], ptk[k][m], -1));
                C[k][m] = new IntVar(store, "C" + k + "_" + m, 0, sumAll);
            }

        // Recurrence: a job starts on machine m once it leaves machine m-1 and the
        // previous job has left machine m.
        for (int k = 0; k < n; k++)
            for (int m = 0; m < M; m++) {
                IntVar start = new IntVar(store, "s" + k + "_" + m, 0, sumAll);
                if (k == 0 && m == 0) {
                    store.impose(new XeqC(start, 0));                          // first job starts at time 0
                    store.impose(new XplusYeqZ(start, ptk[k][m], C[k][m]));
                    continue;
                }
                if (k == 0) {
                    // only the previous machine constrains the start
                    store.impose(new XplusYeqZ(start, ptk[k][m], C[k][m]));
                    store.impose(new Max(new IntVar[]{C[k][m - 1]}, start));
                } else if (m == 0) {
                    store.impose(new XplusYeqZ(start, ptk[k][m], C[k][m]));
                    store.impose(new Max(new IntVar[]{C[k - 1][m]}, start));
                } else {
                    store.impose(new XplusYeqZ(start, ptk[k][m], C[k][m]));
                    store.impose(new Max(new IntVar[]{C[k - 1][m], C[k][m - 1]}, start));
                }
            }

        IntVar makespan = C[n - 1][M - 1];
        return new Model().put("makespan", makespan).minimize(makespan);
    }
}
