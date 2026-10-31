// Birthday coins: Tommy got 15 coins (half-crowns, shillings and sixpences)
// totalling 1 pound 5 shillings 6 pence. Find the number of half-crowns.
//
// The money total is a constant of the problem statement: 1 pound = 240 pence,
// 5 shillings = 60 pence, 6 pence, so 306 pence in all. Coin values are
// 30 pence (half-crown), 12 pence (shilling) and 6 pence (sixpence).
import org.jacop.constraints.*;
import org.jacop.core.*;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        final int coins = 15;
        final int pence = 306;

        // halfCrowns is the declared output; shillings and sixpences are auxiliary counts
        IntVar halfCrowns = new IntVar(store, "half_crowns", 0, coins);
        IntVar shillings = new IntVar(store, "shillings", 0, coins);
        IntVar sixpences = new IntVar(store, "sixpences", 0, coins);

        // the 15 coins in total
        store.impose(new LinearInt(new IntVar[]{halfCrowns, shillings, sixpences},
                new int[]{1, 1, 1}, "==", coins));

        // the coins add up to 1 pound 5 shillings 6 pence
        store.impose(new LinearInt(new IntVar[]{halfCrowns, shillings, sixpences},
                new int[]{30, 12, 6}, "==", pence));

        return new Model().put("half_crowns", halfCrowns);
    }
}
