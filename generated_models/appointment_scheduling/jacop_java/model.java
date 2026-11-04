// Appointment scheduling: schedule every person into an interview slot, using their free-busy schedule.
// m[i][j] = 1 means person i is free in slot j. Each person gets exactly one slot,
// each slot holds at most one person, and a person can only be given a slot they are free in.
// x[i][j] = 1 means person i is assigned to slot j.

import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XeqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray free = inst.getJSONArray("m");
        int people = free.length();                       // number of people, from the instance
        int slots = free.getJSONArray(0).length();        // number of slots, from the instance

        // x[i][j]: person i is assigned to slot j
        BooleanVar[][] x = new BooleanVar[people][slots];
        for (int i = 0; i < people; i++) {
            JSONArray row = free.getJSONArray(i);
            for (int j = 0; j < slots; j++) {
                x[i][j] = new BooleanVar(store, "x" + i + "_" + j);
                // a person cannot be given a slot they are busy in
                if (row.getInt(j) == 0) {
                    store.impose(new XeqC(x[i][j], 0));
                }
            }
        }

        int[] ones = new int[slots];
        for (int j = 0; j < slots; j++) ones[j] = 1;
        int[] onesP = new int[people];
        for (int i = 0; i < people; i++) onesP[i] = 1;

        // every person is assigned exactly one slot
        for (int i = 0; i < people; i++) {
            store.impose(new LinearInt(x[i], ones, "==", 1));
        }

        // every slot holds at most one person
        for (int j = 0; j < slots; j++) {
            BooleanVar[] column = new BooleanVar[people];
            for (int i = 0; i < people; i++) column[i] = x[i][j];
            store.impose(new LinearInt(column, onesP, "<=", 1));
        }

        Model model = new Model();
        return model.put("x", x);
    }
}
