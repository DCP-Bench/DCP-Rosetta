// Traffic lights: eight lights at a four-way junction. Vehicle lights V1..V4 take
// states 0..3 (0=red, 1=red-yellow, 2=green, 3=yellow); pedestrian lights P1..P4 take
// states 0..1 (0=red, 1=green). For i = 1..4 (with V5 = V1 and P5 = P1), the tuple
// (V_i, P_i, V_{i+1}, P_{i+1}) must be one of the safe combinations listed in the instance.
// lights = [V1, V2, V3, V4, P1, P2, P3, P4].
import org.jacop.constraints.table.Table;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // the safe combinations (V_i, P_i, V_i+1, P_i+1), from the instance
        JSONArray rows = inst.getJSONArray("allowed_tuples");
        int[][] allowed = new int[rows.length()][4];
        for (int r = 0; r < rows.length(); r++) {
            JSONArray row = rows.getJSONArray(r);
            for (int c = 0; c < 4; c++) {
                allowed[r][c] = row.getInt(c);
            }
        }

        // vehicle lights take states 0..3, pedestrian lights states 0..1
        IntVar[] v = new IntVar[4];
        IntVar[] p = new IntVar[4];
        for (int i = 0; i < 4; i++) {
            v[i] = new IntVar(store, "V" + (i + 1), 0, 3);
            p[i] = new IntVar(store, "P" + (i + 1), 0, 1);
        }

        // for each road crossing i (the last one wraps round to light 1), the pair of
        // light states must be a safe combination from the instance
        for (int i = 0; i < 4; i++) {
            int next = (i + 1) % 4;
            IntVar[] scope = new IntVar[]{v[i], p[i], v[next], p[next]};
            store.impose(new Table(scope, allowed));
        }

        // the output order is V1..V4 then P1..P4
        IntVar[] lights = new IntVar[8];
        for (int i = 0; i < 4; i++) {
            lights[i] = v[i];
            lights[4 + i] = p[i];
        }
        return new Model().put("lights", lights);
    }
}
