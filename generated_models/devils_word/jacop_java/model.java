// Devil's word (666): put a + or - sign in front of every integer of arr so that the
// signed values sum to total. result[i] is arr[i] with its chosen sign.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XmulCeqZ;
import org.jacop.constraints.XplusCeqZ;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray arr = inst.getJSONArray("arr");   // the integers, from the instance
        int total = inst.getInt("total");           // the target sum, from the instance
        int n = arr.length();

        IntVar[] result = new IntVar[n];
        int[] ones = new int[n];
        for (int i = 0; i < n; i++) {
            int v = arr.getInt(i);
            int mag = Math.abs(v);
            // pos[i] = 1 when the sign of arr[i] is +, 0 when it is -
            BooleanVar pos = new BooleanVar(store, "pos_" + i);
            // u = 2 * v * pos is v or 0 (the sign is +), and
            // result + v = u gives result = v when pos = 1 and result = -v when pos = 0
            IntVar u = new IntVar(store, Math.min(0, 2 * v), Math.max(0, 2 * v));
            store.impose(new XmulCeqZ(pos, 2 * v, u));
            result[i] = new IntVar(store, -mag, mag);
            store.impose(new XplusCeqZ(result[i], v, u));
            ones[i] = 1;
        }

        // the signed values sum to the target total
        store.impose(new LinearInt(result, ones, "==", total));

        return new Model().put("result", result);
    }
}
