import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

// Select exactly m of the numbers so that the selected numbers sum to zero.
// indices[i] is true when nums[i] is selected. m is read from the instance.
public class Submission {
    public static Model build(JSONObject instance, Store store) {
        JSONArray numsJson = instance.getJSONArray("nums");
        int m = instance.getInt("m");
        int n = numsJson.length();

        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = numsJson.getInt(i);

        BooleanVar[] x = new BooleanVar[n];
        for (int i = 0; i < n; i++) x[i] = new BooleanVar(store, "x" + i);

        // Exactly m elements are selected.
        int[] ones = new int[n];
        java.util.Arrays.fill(ones, 1);
        store.impose(new LinearInt(x, ones, "==", m));

        // The selected numbers sum to zero.
        store.impose(new LinearInt(x, nums, "==", 0));

        return new Model().put("indices", x);
    }
}
