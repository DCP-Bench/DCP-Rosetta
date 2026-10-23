// Bananas: buy 100 fruits (bananas, oranges, mangoes, apples) for exactly 100 dollars,
// with at least one of each kind. Prices: 5 bananas for 3 dollars, 7 oranges for 5 dollars,
// 9 mangoes for 7 dollars, 3 apples for 9 dollars. Bananas and apples should be bought in
// the smallest quantity, so minimise bananas + apples.
// Outputs: "bananas", "oranges", "mangoes", "apples".
//
// The problem fixes its totals (100 fruits, 100 dollars), so they are constants here, and the
// instance has no data fields.
// Costs are scaled by 315 dollars-units (315 = lcm of 5, 7, 9 and 3) so that every unit price
// is an integer: a banana is 189, an orange 225, a mango 245 and an apple 945 (in 1/315 dollar).
// The budget of 100 dollars is then 31500.
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        final int fruits = 100;       // fruits to buy
        final int budget = 31500;     // 100 dollars in 1/315 dollar units

        IntVar bananas = new IntVar(store, "bananas", 1, fruits);
        IntVar oranges = new IntVar(store, "oranges", 1, fruits);
        IntVar mangoes = new IntVar(store, "mangoes", 1, fruits);
        IntVar apples = new IntVar(store, "apples", 1, fruits);
        IntVar[] all = {bananas, oranges, mangoes, apples};

        // Exactly 100 fruits in total.
        store.impose(new LinearInt(all, new int[]{1, 1, 1, 1}, "==", fruits));

        // Exactly 100 dollars spent: 189 per banana, 225 per orange, 245 per mango, 945 per apple.
        store.impose(new LinearInt(all, new int[]{189, 225, 245, 945}, "==", budget));

        // Objective: bananas + apples, which the problem asks to keep as small as possible.
        IntVar few = new IntVar(store, "bananas_plus_apples", 2, 2 * fruits);
        store.impose(new LinearInt(new IntVar[]{bananas, apples, few}, new int[]{1, 1, -1}, "==", 0));

        return new Model()
            .put("bananas", bananas).put("oranges", oranges)
            .put("mangoes", mangoes).put("apples", apples)
            .minimize(few);
    }
}
