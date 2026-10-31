// Dinner: choose 1-6 grandparents, 1-10 parents and 1-40 children so that 20 people
// go to dinner and the bill is exactly $20 (grandparents $3, parents $2, children $0.50).
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject instance, Store store) {
        IntVar grandparents = new IntVar(store, 1, 6);
        IntVar parents = new IntVar(store, 1, 10);
        IntVar children = new IntVar(store, 1, 40);

        // There must be 20 people at dinner.
        store.impose(new LinearInt(
            new IntVar[]{grandparents, parents, children}, new int[]{1, 1, 1}, "==", 20));

        // The bill is $20. To avoid fractions, count in half dollars: a grandparent costs 6,
        // a parent 4 and a child 1, and the total must be 40.
        store.impose(new LinearInt(
            new IntVar[]{grandparents, parents, children}, new int[]{6, 4, 1}, "==", 40));

        Model m = new Model()
            .put("children", children)
            .put("grandparents", grandparents)
            .put("parents", parents);
        m.search(new IntVar[]{grandparents, parents, children}, null, null);
        return m;
    }
}
