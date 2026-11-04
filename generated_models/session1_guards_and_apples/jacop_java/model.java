// The boy passes num_gates gates. At each gate he bribes the guard with half of his apples plus one,
// which must be a whole number, so his apple count a[i] is even at every gate. After the last gate he
// has a[num_gates] apples; he gives one to the girl and then has none, so a[num_gates] = 1.
// Output apples[i] = number of apples before gate i (i < num_gates), and apples[num_gates] after the last gate.
//
// Each gate leaves a[i+1] = a[i]/2 - 1, which is the constraint a[i] - 2*a[i+1] = 2 (this also forces a[i] even).
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XeqC;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int gates = inst.getInt("num_gates");

        // loose upper bound: the count at most halves at each gate, so 4 * 2^gates covers every value
        int upper = 1 << (gates + 2);
        IntVar[] apples = new IntVar[gates + 1];
        for (int i = 0; i <= gates; i++) {
            apples[i] = new IntVar(store, "apples_" + i, 0, upper);
        }

        // after the last gate he has one apple left, which he gives to the girl
        store.impose(new XeqC(apples[gates], 1));

        // gate i: he gives half of his apples plus one, leaving a[i]/2 - 1 apples
        // (a[i] - 2*a[i+1] = 2 means a[i] = 2 * (a[i+1] + 1), so a[i] is even)
        for (int i = 0; i < gates; i++) {
            store.impose(new LinearInt(new IntVar[]{apples[i], apples[i + 1]}, new int[]{1, -2}, "==", 2));
        }

        return new Model().put("apples", apples);
    }
}
