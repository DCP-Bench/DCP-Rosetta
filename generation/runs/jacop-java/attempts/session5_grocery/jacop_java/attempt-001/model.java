// Grocery prices: num_items item prices in cents, whose sum and whose product both equal total_price.
// Instance fields: num_items (how many items), total_price (the total in cents, which is the sum and the product).
// Output prices[i] = price of item i in cents. Every price is a positive whole number.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int items = inst.getInt("num_items");
        int total = inst.getInt("total_price");

        // prices[i]: price of item i in cents; a price is at least 1 and at most the total
        IntVar[] prices = new IntVar[items];
        int[] ones = new int[items];
        for (int i = 0; i < items; i++) {
            prices[i] = new IntVar(store, "price_" + i, 1, total);
            ones[i] = 1;
        }

        // the prices add up to the total: sum of prices = total_price
        store.impose(new LinearInt(prices, ones, "==", total));

        // the prices multiply to the total: running product over the items, ending at total_price
        // (every price is at least 1, so each partial product is at most the final product, which is total)
        IntVar product = prices[0];
        for (int i = 1; i < items; i++) {
            IntVar next = new IntVar(store, 1, total);
            store.impose(new XmulYeqZ(product, prices[i], next));
            product = next;
        }
        store.impose(new XeqC(product, total));

        return new Model().put("prices", prices);
    }
}
