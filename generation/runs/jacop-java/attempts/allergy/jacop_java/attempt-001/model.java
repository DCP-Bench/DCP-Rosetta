// Allergy: four friends (Debra = 0, Janet = 1, Hugh = 2, Rick = 3) each have a different
// allergy (eggs, mold, nuts, ragweed) and a different surname (Baxter, Lemon, Malone, Fleet).
// Each output is the friend number (0..3) who has that allergy or surname.
// Outputs: eggs, mold, nuts, ragweed, baxter, lemon, malone, fleet.
//
// The problem has no instance data: the friends and the clues are fixed.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.XeqY;
import org.jacop.constraints.XneqC;
import org.jacop.constraints.XeqC;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    // Friend numbers from the problem statement.
    static final int DEBRA = 0, JANET = 1, HUGH = 2, RICK = 3;

    public static Model build(JSONObject inst, Store store) {
        IntVar eggs = new IntVar(store, "eggs", 0, 3);
        IntVar mold = new IntVar(store, "mold", 0, 3);
        IntVar nuts = new IntVar(store, "nuts", 0, 3);
        IntVar ragweed = new IntVar(store, "ragweed", 0, 3);
        IntVar baxter = new IntVar(store, "baxter", 0, 3);
        IntVar lemon = new IntVar(store, "lemon", 0, 3);
        IntVar malone = new IntVar(store, "malone", 0, 3);
        IntVar fleet = new IntVar(store, "fleet", 0, 3);

        // Each allergy belongs to a different friend.
        store.impose(new Alldifferent(new IntVar[]{eggs, mold, nuts, ragweed}));
        // Each surname belongs to a different friend.
        store.impose(new Alldifferent(new IntVar[]{baxter, lemon, malone, fleet}));

        // Rick is not allergic to mold.
        store.impose(new XneqC(mold, RICK));
        // Baxter is allergic to eggs: the same friend has both.
        store.impose(new XeqY(baxter, eggs));
        // Hugh is neither surnamed Lemon nor Fleet.
        store.impose(new XneqC(lemon, HUGH));
        store.impose(new XneqC(fleet, HUGH));
        // Debra is allergic to ragweed.
        store.impose(new XeqC(ragweed, DEBRA));
        // Janet is not surnamed Lemon, and is neither allergic to eggs nor to mold.
        store.impose(new XneqC(lemon, JANET));
        store.impose(new XneqC(eggs, JANET));
        store.impose(new XneqC(mold, JANET));

        return new Model()
            .put("baxter", baxter).put("eggs", eggs).put("fleet", fleet).put("lemon", lemon)
            .put("malone", malone).put("mold", mold).put("nuts", nuts).put("ragweed", ragweed);
    }
}
