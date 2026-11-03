// Climbing stairs: a stair of n steps, and each move climbs between m1 and m2 steps.
// steps[i] is the number of steps taken at move i: a value in m1..m2 while the top is
// not yet reached, and 0 once it is reached. Every sequence that climbs exactly n steps
// is a solution.
import org.jacop.constraints.*;
import org.jacop.core.*;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // n, m1 and m2 come from the instance; nothing here is fixed to the example
        int n = inst.getInt("n");
        int m1 = inst.getInt("m1");
        int m2 = inst.getInt("m2");

        // steps[i]: steps taken at move i, 0..m2 (the lower bound m1 is enforced below)
        IntVar[] steps = new IntVar[n];
        // height[i]: height reached after i moves, 0..n; height[0] = 0 at the bottom
        IntVar[] height = new IntVar[n + 1];
        height[0] = new IntVar(store, "height0", 0, 0);

        for (int i = 0; i < n; i++) {
            steps[i] = new IntVar(store, "steps" + i, 0, m2);
            height[i + 1] = new IntVar(store, "height" + (i + 1), 0, n);

            // height grows by the steps taken at this move
            store.impose(new XplusYeqZ(height[i], steps[i], height[i + 1]));

            // top[i] = 1 when the top is already reached before move i
            BooleanVar top = new BooleanVar(store, "top" + i);
            store.impose(new Reified(new XeqC(height[i], n), top));

            // once at the top, no more steps are taken: steps[i] = 0
            store.impose(new IfThen(new XeqC(top, 1), new XeqC(steps[i], 0)));
            // before the top, a move is between m1 and m2 steps
            store.impose(new IfThen(new XeqC(top, 0), new XgteqC(steps[i], m1)));
        }

        // the moves together climb exactly the n steps of the stair
        store.impose(new XeqC(height[n], n));

        Model m = new Model().put("steps", steps);
        // label the step values first; the heights and flags follow from them
        m.search(steps, null, null);
        return m;
    }
}
