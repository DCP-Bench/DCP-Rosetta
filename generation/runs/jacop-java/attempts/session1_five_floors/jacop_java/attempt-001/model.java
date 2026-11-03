// Five floors: Baker, Cooper, Fletcher, Miller and Smith each live on a different one of floors 1..5.
// Floors are numbered 1 (lowest) to 5 (highest); the instance carries no data.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XltY;
import org.jacop.constraints.XneqY;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject instance, Store store) {
        // B, C, F, M, S: the floor each person lives on
        IntVar B = new IntVar(store, "B", 1, 5);  // Baker
        IntVar C = new IntVar(store, "C", 1, 5);  // Cooper
        IntVar F = new IntVar(store, "F", 1, 5);  // Fletcher
        IntVar M = new IntVar(store, "M", 1, 5);  // Miller
        IntVar S = new IntVar(store, "S", 1, 5);  // Smith

        // they all live on different floors
        IntVar[] people = {B, C, F, M, S};
        for (int p = 0; p < people.length; p++) {
            for (int q = p + 1; q < people.length; q++) {
                store.impose(new XneqY(people[p], people[q]));
            }
        }

        // Baker does not live on the fifth floor
        store.impose(new LinearInt(new IntVar[]{B}, new int[]{1}, "!=", 5));
        // Cooper does not live on the first floor
        store.impose(new LinearInt(new IntVar[]{C}, new int[]{1}, "!=", 1));
        // Fletcher does not live on either the fifth or the first floor
        store.impose(new LinearInt(new IntVar[]{F}, new int[]{1}, "!=", 5));
        store.impose(new LinearInt(new IntVar[]{F}, new int[]{1}, "!=", 1));
        // Miller lives on a higher floor than Cooper
        store.impose(new XltY(C, M));
        // Smith does not live on a floor adjacent to Fletcher: |S - F| != 1
        store.impose(new LinearInt(new IntVar[]{S, F}, new int[]{1, -1}, "!=", 1));
        store.impose(new LinearInt(new IntVar[]{S, F}, new int[]{1, -1}, "!=", -1));
        // Fletcher does not live on a floor adjacent to Cooper's: |F - C| != 1
        store.impose(new LinearInt(new IntVar[]{F, C}, new int[]{1, -1}, "!=", 1));
        store.impose(new LinearInt(new IntVar[]{F, C}, new int[]{1, -1}, "!=", -1));

        Model model = new Model().put("B", B).put("C", C).put("F", F).put("M", M).put("S", S);
        return model;
    }
}
