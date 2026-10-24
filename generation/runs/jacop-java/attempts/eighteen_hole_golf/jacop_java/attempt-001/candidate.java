// Eighteen-hole golf course: choose a length of 3, 4 or 5 for each of the 18 holes
// so that the total length of the course is 72. Output: holes[i] = length of hole i.

import org.jacop.constraints.SumInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // The problem fixes 18 holes and a total length of 72 (problem constants, not instance data).
        int numHoles = 18;
        int totalLength = 72;

        // holes[i] = length of hole i, each one of 3, 4 or 5.
        IntVar[] holes = new IntVar[numHoles];
        for (int i = 0; i < numHoles; i++) {
            holes[i] = new IntVar(store, "hole" + i, 3, 5);
        }

        // The total length of the course is 72: the sum of all hole lengths equals 72.
        IntVar total = new IntVar(store, "total", totalLength, totalLength);
        store.impose(new SumInt(holes, "==", total));

        return new Model().put("holes", holes);
    }
}
