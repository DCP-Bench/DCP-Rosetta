import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

// Each suspect x has a guilt variable g_x (1 = guilty). The statement of x is
// true exactly when x is innocent, so truth(x) = 1 - g_x for every suspect.
// The suspects are ordered artie, bill, crackitt, dodgy, edgy, fingers.
public class Submission {
    public static Model build(JSONObject instance, Store store) {
        BooleanVar artie = new BooleanVar(store, "artie");
        BooleanVar bill = new BooleanVar(store, "bill");
        BooleanVar crackitt = new BooleanVar(store, "crackitt");
        BooleanVar dodgy = new BooleanVar(store, "dodgy");
        BooleanVar edgy = new BooleanVar(store, "edgy");
        BooleanVar fingers = new BooleanVar(store, "fingers");

        IntVar[] guilt = {artie, bill, crackitt, dodgy, edgy, fingers};
        int[] ones = {1, 1, 1, 1, 1, 1};

        // The car holds two, so at most two are guilty. At least one person did it.
        store.impose(new LinearInt(guilt, ones, "<=", 2));
        store.impose(new LinearInt(guilt, ones, ">=", 1));

        // Artie: "It wasn't me." Truth is 1 - artie, which is the innocence
        // requirement itself, so it adds no constraint.

        // Bill: "Crackitt was in it up to his neck." Truth is crackitt.
        // Bill must tell the truth iff innocent: crackitt == 1 - bill.
        store.impose(new LinearInt(new IntVar[]{bill, crackitt}, new int[]{1, 1}, "==", 1));

        // Crackitt: "No I wasn't." Truth is 1 - crackitt, the innocence requirement itself.

        // Dodgy: "If Crackitt did it, Bill did it with him." Truth is (crackitt -> bill).
        // sDodgy <-> (crackitt - bill <= 0); truth must equal 1 - dodgy.
        BooleanVar sDodgy = new BooleanVar(store, "sDodgy");
        store.impose(new Reified(
            new LinearInt(new IntVar[]{crackitt, bill}, new int[]{1, -1}, "<=", 0), sDodgy));
        store.impose(new LinearInt(new IntVar[]{sDodgy, dodgy}, new int[]{1, 1}, "==", 1));

        // Edgy: "Nobody did it alone." Truth is (number of guilty != 1).
        // sEdgy <-> (sum of guilt != 1); truth must equal 1 - edgy.
        BooleanVar sEdgy = new BooleanVar(store, "sEdgy");
        store.impose(new Reified(new LinearInt(guilt, ones, "!=", 1), sEdgy));
        store.impose(new LinearInt(new IntVar[]{sEdgy, edgy}, new int[]{1, 1}, "==", 1));

        // Fingers: "That's right: it was Artie and Dodgy together."
        // Truth is: guilty set is exactly {artie, dodgy}. Written as
        // artie + dodgy - bill - crackitt - edgy - fingers == 2, which holds only when
        // artie and dodgy are guilty and the other four are not.
        // sFingers <-> that equality; truth must equal 1 - fingers.
        BooleanVar sFingers = new BooleanVar(store, "sFingers");
        store.impose(new Reified(new LinearInt(
            new IntVar[]{artie, dodgy, bill, crackitt, edgy, fingers},
            new int[]{1, 1, -1, -1, -1, -1}, "==", 2), sFingers));
        store.impose(new LinearInt(new IntVar[]{sFingers, fingers}, new int[]{1, 1}, "==", 1));

        return new Model()
            .put("artie", artie)
            .put("bill", bill)
            .put("crackitt", crackitt)
            .put("dodgy", dodgy)
            .put("edgy", edgy)
            .put("fingers", fingers);
    }
}
