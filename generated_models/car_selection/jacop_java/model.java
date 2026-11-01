// Car selection: assign participants to cars so that the number of assignments
// is maximal. A participant may only take a car they are interested in, each
// participant gets at most one car, and each car goes to at most one participant.
// assignments[i][j] = 1 if participant i is assigned to car j.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XeqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // the interest matrix: rows are participants, columns are cars
        JSONArray pa = inst.getJSONArray("possible_assignments");
        int participants = pa.length();
        int cars = participants > 0 ? pa.getJSONArray(0).length() : 0;

        // one Boolean per participant and car
        BooleanVar[][] a = new BooleanVar[participants][cars];
        for (int i = 0; i < participants; i++) {
            for (int j = 0; j < cars; j++) {
                a[i][j] = new BooleanVar(store, "a" + i + "_" + j);
                // a participant can only be assigned to a car they are interested in
                if (pa.getJSONArray(i).getInt(j) == 0) {
                    store.impose(new XeqC(a[i][j], 0));
                }
            }
        }

        // each participant is assigned to at most one car
        for (int i = 0; i < participants; i++) {
            IntVar[] row = new IntVar[cars];
            int[] ones = new int[cars];
            for (int j = 0; j < cars; j++) {
                row[j] = a[i][j];
                ones[j] = 1;
            }
            store.impose(new LinearInt(row, ones, "<=", 1));
        }

        // each car is assigned to at most one participant
        for (int j = 0; j < cars; j++) {
            IntVar[] col = new IntVar[participants];
            int[] ones = new int[participants];
            for (int i = 0; i < participants; i++) {
                col[i] = a[i][j];
                ones[i] = 1;
            }
            store.impose(new LinearInt(col, ones, "<=", 1));
        }

        // the objective is the total number of assignments, to be maximised
        IntVar[] all = new IntVar[participants * cars];
        for (int i = 0; i < participants; i++) {
            for (int j = 0; j < cars; j++) {
                all[i * cars + j] = a[i][j];
            }
        }
        IntVar total = new IntVar(store, 0, Math.min(participants, cars));
        // total = sum of all assignment Booleans
        store.impose(new SumInt(all, "==", total));

        Model m = new Model().put("assignments", a);
        return m.maximize(total);
    }
}
