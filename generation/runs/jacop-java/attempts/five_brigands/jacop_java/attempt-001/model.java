// Five brigands: A, B, C, D, E are the doubloons of Alfonso, Benito, Carlos, Diego and Esteban.
// Together they hold exactly 200 doubloons, and with Alfonso's share times 12, Benito's times 3,
// Carlos's unchanged, Diego's halved and Esteban's divided by 3, the total is still 200.
// Each brigand has at least one doubloon. Multiplying the second equation by 6 keeps every
// coefficient an integer:
//     A + B + C + D + E = 200
//     72A + 18B + 6C + 3D + 2E = 1200
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Each brigand has at least one doubloon. The total of 200 bounds each share by 196.
        IntVar A = new IntVar(store, "A", 1, 196);
        IntVar B = new IntVar(store, "B", 1, 196);
        IntVar C = new IntVar(store, "C", 1, 196);
        IntVar D = new IntVar(store, "D", 1, 196);
        IntVar E = new IntVar(store, "E", 1, 196);
        IntVar[] shares = {A, B, C, D, E};

        // The brigands together hold exactly 200 doubloons.
        store.impose(new LinearInt(shares, new int[]{1, 1, 1, 1, 1}, "==", 200));

        // The same total after the changes (equation multiplied by 6 to clear the halves and thirds).
        store.impose(new LinearInt(shares, new int[]{72, 18, 6, 3, 2}, "==", 1200));

        return new Model().put("A", A).put("B", B).put("C", C).put("D", D).put("E", E);
    }
}
