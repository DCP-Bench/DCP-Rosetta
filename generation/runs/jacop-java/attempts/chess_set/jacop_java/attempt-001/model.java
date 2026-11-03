// Chess sets: a joinery makes small and large boxwood chess sets each week and
// wants the number of each that maximises profit, under lathe and boxwood limits.
import org.jacop.constraints.*;
import org.jacop.core.*;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // problem constants from the statement
        final int latheHours = 4 * 40;   // four lathes, 40 hours each per week
        final int boxwoodKg = 200;       // boxwood available per week
        final int smallLathe = 3, largeLathe = 2;    // lathe hours per set
        final int smallWood = 1, largeWood = 3;      // kg of boxwood per set
        final int smallProfit = 5, largeProfit = 20; // dollars per set

        // upper bounds on the number of sets, from the lathe limit alone
        IntVar small = new IntVar(store, "small_set", 0, latheHours / smallLathe);
        IntVar large = new IntVar(store, "large_set", 0, latheHours / largeLathe);

        // lathe-hours: a small set uses 3 hours, a large set 2 hours
        store.impose(new LinearInt(new IntVar[]{small, large},
                new int[]{smallLathe, largeLathe}, "<=", latheHours));

        // boxwood: a small set uses 1 kg, a large set 3 kg
        store.impose(new LinearInt(new IntVar[]{small, large},
                new int[]{smallWood, largeWood}, "<=", boxwoodKg));

        // the profit is 5 dollars per small set and 20 dollars per large set
        IntVar profit = new IntVar(store, "max_profit", 0,
                smallProfit * (latheHours / smallLathe) + largeProfit * (latheHours / largeLathe));
        store.impose(new LinearInt(new IntVar[]{small, large, profit},
                new int[]{smallProfit, largeProfit, -1}, "==", 0));

        return new Model().put("small_set", small).put("large_set", large)
                .put("max_profit", profit).maximize(profit);
    }
}
