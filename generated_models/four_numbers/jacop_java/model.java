// Four numbers: find three integers x1, x2, x3 in 1..10 such that every given number
// is the sum of a subset of {x1, x2, x3}. Output x: the three integers.
// For each given number y, a 0/1 choice b[j][i] says whether x[i] is in its subset,
// and the chosen parts b[j][i] * x[i] add up to y.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray numbers = inst.getJSONArray("numbers");   // the given numbers, 3 or 4 of them
        int count = numbers.length();
        int parts = 3;                                       // the answer has three integers

        // The three integers, each between 1 and 10 as the problem states.
        IntVar[] x = new IntVar[parts];
        for (int i = 0; i < parts; i++) {
            x[i] = new IntVar(store, "x" + i, 1, 10);
        }

        // For each given number y: part[j][i] = b[j][i] * x[i], with b a 0/1 choice of
        // whether x[i] takes part in the sum for y. Then y = sum of the parts.
        for (int j = 0; j < count; j++) {
            IntVar[] part = new IntVar[parts];
            int[] weights = new int[parts];
            for (int i = 0; i < parts; i++) {
                BooleanVar b = new BooleanVar(store, "b" + j + "_" + i);
                part[i] = new IntVar(store, "p" + j + "_" + i, 0, 10);
                // part = b * x[i]
                store.impose(new XmulYeqZ(b, x[i], part[i]));
                weights[i] = 1;
            }
            // The chosen parts sum to the given number.
            store.impose(new LinearInt(part, weights, "==", numbers.getInt(j)));
        }

        Model m = new Model().put("x", x);
        m.search(x, null, null);             // label the three integers first, then the choices
        return m;
    }
}
