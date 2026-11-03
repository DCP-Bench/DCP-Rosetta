// ISBN-13 validation and check digit: fill in the unknown digits (-1 in the input)
// of a 13-digit ISBN so that it is valid. The number starts with 978 or 979, and
// the alternating weighted sum of its digits (weights 1, 3, 1, 3, ...) is a multiple of 10.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Or;
import org.jacop.constraints.XeqC;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // The given digits come from the instance; -1 marks an unknown digit.
        JSONArray init = inst.getJSONArray("isbn_init");
        int len = init.length(); // 13 for an ISBN-13

        // digit[i] is the i-th digit of the ISBN, 0..9.
        IntVar[] digit = new IntVar[len];
        for (int i = 0; i < len; i++) {
            digit[i] = new IntVar(store, "d" + i, 0, 9);
            int given = init.getInt(i);
            // A given digit is fixed to its value; an unknown one stays free in 0..9.
            if (given >= 0) {
                store.impose(new XeqC(digit[i], given));
            }
        }

        // The ISBN starts with the prefix 978 or 979: digits 0 and 1 are 9 and 7,
        // and digit 2 is 8 or 9.
        store.impose(new XeqC(digit[0], 9));
        store.impose(new XeqC(digit[1], 7));
        store.impose(new Or(new XeqC(digit[2], 8), new XeqC(digit[2], 9)));

        // Check digit rule: the weighted sum of the digits, with weight 1 on even
        // positions and weight 3 on odd positions, is a multiple of 10. The multiple
        // is k, which is linked to the sum by the weight -10 on k.
        // The sum is at most 9 * (7*1 + 6*3) = 225, so k is at most 22.
        IntVar k = new IntVar(store, "k", 0, 30);
        IntVar[] vars = new IntVar[len + 1];
        int[] weights = new int[len + 1];
        for (int i = 0; i < len; i++) {
            vars[i] = digit[i];
            weights[i] = (i % 2 == 0) ? 1 : 3;
        }
        vars[len] = k;
        weights[len] = -10;
        store.impose(new LinearInt(vars, weights, "==", 0));

        // Output isbn is the completed ISBN.
        return new Model().put("isbn", digit);
    }
}
