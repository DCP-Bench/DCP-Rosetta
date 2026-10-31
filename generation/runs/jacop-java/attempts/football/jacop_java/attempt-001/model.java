// Football squad: choose players from the groups so that the total price is as high as possible
// without going over GBP 30 million. Output: z = total price of the chosen players in GBP thousands.
//
// Prices are given in GBP millions with at most three decimals, so they are scaled to GBP
// thousands (0.73 -> 730) to stay in integers. The budget 30 million is 30000 thousands.

import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Problem data from the description, in GBP thousands.
        int[] goalkeeperPrice = {730, 1280, 3880};
        int[] defenderPrice = {920, 1310, 1620, 2410, 2790, 3280, 3910, 4570};
        int[] midfielderPrice = {1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130};
        int[] strikerPrice = {4460, 6470, 7780, 8390, 9500};

        // The chairman's limit: GBP 30 million = 30000 thousands.
        int budget = 30000;
        // The squad must contain at least eleven players in total.
        int minPlayers = 11;

        // Each player is one Boolean: 1 = bought. Players are listed group by group.
        int total = goalkeeperPrice.length + defenderPrice.length
                + midfielderPrice.length + strikerPrice.length;
        BooleanVar[] buy = new BooleanVar[total];
        int[] price = new int[total];
        int pos = 0;
        int goalkeeperStart = pos;
        for (int p : goalkeeperPrice) { buy[pos] = new BooleanVar(store, "g" + pos); price[pos++] = p; }
        int defenderStart = pos;
        for (int p : defenderPrice) { buy[pos] = new BooleanVar(store, "d" + pos); price[pos++] = p; }
        int midfielderStart = pos;
        for (int p : midfielderPrice) { buy[pos] = new BooleanVar(store, "m" + pos); price[pos++] = p; }
        int strikerStart = pos;
        for (int p : strikerPrice) { buy[pos] = new BooleanVar(store, "s" + pos); price[pos++] = p; }

        // Group rules: exactly 1 goalkeeper, at least 2 defenders, at least 3 midfielders,
        // at least 2 strikers.
        postGroup(store, buy, goalkeeperStart, goalkeeperPrice.length, "==", 1);
        postGroup(store, buy, defenderStart, defenderPrice.length, ">=", 2);
        postGroup(store, buy, midfielderStart, midfielderPrice.length, ">=", 3);
        postGroup(store, buy, strikerStart, strikerPrice.length, ">=", 2);

        // At least eleven players in total.
        int[] ones = new int[total];
        java.util.Arrays.fill(ones, 1);
        store.impose(new LinearInt(buy, ones, ">=", minPlayers));

        // z = total price of the chosen players, in GBP thousands, at most the budget.
        IntVar z = new IntVar(store, "z", 0, budget);
        IntVar[] priceVars = new IntVar[total + 1];
        int[] priceWeights = new int[total + 1];
        for (int i = 0; i < total; i++) {
            priceVars[i] = buy[i];
            priceWeights[i] = price[i];
        }
        priceVars[total] = z;
        priceWeights[total] = -1;
        // sum of price_i * buy_i - z = 0
        store.impose(new LinearInt(priceVars, priceWeights, "==", 0));

        return new Model().put("z", z).maximize(z);
    }

    // Posts a count rule over the players of one group: the number of bought players of the
    // group compares to the bound (for example, "==" 1 for the goalkeeper).
    private static void postGroup(Store store, BooleanVar[] buy, int start, int size,
                                  String relation, int bound) {
        IntVar[] group = new IntVar[size];
        int[] ones = new int[size];
        for (int i = 0; i < size; i++) {
            group[i] = buy[start + i];
            ones[i] = 1;
        }
        store.impose(new LinearInt(group, ones, relation, bound));
    }
}
