// Hardy's 1729 square: find four different numbers a, b, c, d between 1 and 100 such that
// a^2 + b^2 = c^2 + d^2. The instance carries no data.
import org.jacop.constraints.XneqY;
import org.jacop.constraints.XplusYeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject instance, Store store) {
        // the four numbers, each between 1 and 100
        IntVar a = new IntVar(store, "a", 1, 100);
        IntVar b = new IntVar(store, "b", 1, 100);
        IntVar c = new IntVar(store, "c", 1, 100);
        IntVar d = new IntVar(store, "d", 1, 100);

        // the four numbers are different
        IntVar[] numbers = {a, b, c, d};
        for (int p = 0; p < numbers.length; p++) {
            for (int q = p + 1; q < numbers.length; q++) {
                store.impose(new XneqY(numbers[p], numbers[q]));
            }
        }

        // squares of the numbers; the sum of the squares of a and b equals that of c and d.
        // Squares reach 10000, well within the int range.
        IntVar aa = new IntVar(store, "a squared", 1, 10000);
        IntVar bb = new IntVar(store, "b squared", 1, 10000);
        IntVar cc = new IntVar(store, "c squared", 1, 10000);
        IntVar dd = new IntVar(store, "d squared", 1, 10000);
        store.impose(new org.jacop.constraints.XmulYeqZ(a, a, aa));
        store.impose(new org.jacop.constraints.XmulYeqZ(b, b, bb));
        store.impose(new org.jacop.constraints.XmulYeqZ(c, c, cc));
        store.impose(new org.jacop.constraints.XmulYeqZ(d, d, dd));

        // a^2 + b^2 = c^2 + d^2
        IntVar sum = new IntVar(store, "sum of squares", 2, 20000);
        store.impose(new XplusYeqZ(aa, bb, sum));
        store.impose(new XplusYeqZ(cc, dd, sum));

        Model model = new Model().put("a", a).put("b", b).put("c", c).put("d", d);
        return model;
    }
}
