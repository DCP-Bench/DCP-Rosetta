// Abbot's puzzle: 100 bushels of corn are shared among 100 people (men, women, children).
// Each man gets 3 bushels, each woman 2, each child 1/2. There are five times as many
// women as men. Find the numbers of men, women and children.
// Outputs: "men", "women", "children".
//
// The problem fixes its totals (100 people, 100 bushels), so they are constants here.
// The instance has no data fields. Bushels are doubled so that a child's half bushel
// is an integer: each man 6, each woman 4, each child 1, total 200.
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        final int people = 100;      // the total number of people, fixed by the problem
        final int bushelsX2 = 200;   // 100 bushels, doubled

        IntVar men = new IntVar(store, "men", 0, people);
        IntVar women = new IntVar(store, "women", 0, people);
        IntVar children = new IntVar(store, "children", 0, people);

        // Everyone is a man, a woman or a child: men + women + children = 100.
        store.impose(new LinearInt(
            new IntVar[]{men, women, children}, new int[]{1, 1, 1}, "==", people));

        // The corn is all distributed: 6 per man, 4 per woman, 1 per child (doubled
        // bushels), totalling 200 = 100 bushels.
        store.impose(new LinearInt(
            new IntVar[]{men, women, children}, new int[]{6, 4, 1}, "==", bushelsX2));

        // There are five times as many women as men: women = 5 * men.
        // Written as 5 * men - women = 0.
        store.impose(new LinearInt(
            new IntVar[]{men, women}, new int[]{5, -1}, "==", 0));

        return new Model().put("men", men).put("women", women).put("children", children);
    }
}
