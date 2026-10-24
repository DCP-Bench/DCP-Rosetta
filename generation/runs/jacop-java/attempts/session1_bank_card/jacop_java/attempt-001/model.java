// Bank card PIN abcd: four digits a, b, c, d, no two the same.
// The two-digit number cd is 3 times the two-digit number ab: 10c + d = 3 * (10a + b).
// The two-digit number da is 2 times the two-digit number bc: 10d + a = 2 * (10b + c).
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {

    public static Model build(JSONObject instance, Store store) {
        IntVar a = new IntVar(store, "a", 0, 9);
        IntVar b = new IntVar(store, "b", 0, 9);
        IntVar c = new IntVar(store, "c", 0, 9);
        IntVar d = new IntVar(store, "d", 0, 9);
        IntVar[] pin = {a, b, c, d};

        // No two digits are the same.
        store.impose(new Alldifferent(pin));

        // cd = 3 * ab, moved to one side: 10c + d - 30a - 3b = 0.
        store.impose(new LinearInt(new IntVar[]{c, d, a, b}, new int[]{10, 1, -30, -3}, "==", 0));
        // da = 2 * bc, moved to one side: 10d + a - 20b - 2c = 0.
        store.impose(new LinearInt(new IntVar[]{d, a, b, c}, new int[]{10, 1, -20, -2}, "==", 0));

        return new Model().put("a", a).put("b", b).put("c", c).put("d", d)
            .search(pin, null, null);
    }
}
