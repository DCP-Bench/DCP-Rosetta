// Curious set of integers: the set {1, 3, 8, 120} has the property that the product of any
// two of its members is one less than a perfect square. Find a number number >= 0 that can
// join the set: for each member a of the set, a * number + 1 must be a perfect square.
// The search range for number is the instance's max_val; the instance's n (the size of the
// completed set, 5) is not needed because the four given members are fixed by the statement.
import org.jacop.constraints.XmulCeqZ;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.constraints.XplusCeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int maxVal = inst.getInt("max_val");

        // The given members of the set (fixed by the statement).
        int[] members = {1, 3, 8, 120};

        // number is the fifth member, between 0 and the instance's bound.
        IntVar number = new IntVar(store, "number", 0, maxVal);

        for (int a : members) {
            // ax = a * number, then sq = ax + 1 must be a perfect square s * s.
            int hiProduct = a * maxVal + 1;
            IntVar ax = new IntVar(store, "ax" + a, 0, a * maxVal);
            IntVar sq = new IntVar(store, "sq" + a, 1, hiProduct);
            // The root of sq is at most floor(sqrt(hiProduct)).
            int hiRoot = (int) Math.floor(Math.sqrt(hiProduct));
            IntVar s = new IntVar(store, "root" + a, 0, hiRoot);

            store.impose(new XmulCeqZ(number, a, ax));   // ax = a * number
            store.impose(new XplusCeqZ(ax, 1, sq));      // sq = a * number + 1
            store.impose(new XmulYeqZ(s, s, sq));        // sq is the square of s
        }

        return new Model().put("number", number);
    }
}
