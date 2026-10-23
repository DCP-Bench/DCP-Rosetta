// Divisible by 1 through 9: a 10-digit number that uses each digit 0 to 9 exactly once, where
// the number formed by its first n digits is divisible by n, for n = 1 to 10.
// The digits are read left to right: digits[0] is the leading digit, digits[9] the last.
// The whole number is 10 digits (above 2^31), so it is reported with putDigits. Its prefixes
// of length 1 to 9 stay below 10^9 and fit in int.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XmulCeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int digitCount = 10;

        // digits[i] is the (i+1)-th digit of the number, each in 0..9, all different.
        // A 10-digit number has a non-zero leading digit, so digits[0] is in 1..9.
        IntVar[] digits = new IntVar[digitCount];
        for (int i = 0; i < digitCount; i++)
            digits[i] = new IntVar(store, "d" + (i + 1), i == 0 ? 1 : 0, 9);
        store.impose(new Alldifferent(digits));

        // prefix[k] is the number formed by the first k digits, for k = 1..9.
        IntVar[] prefix = new IntVar[digitCount];
        prefix[0] = digits[0];
        for (int k = 2; k <= 9; k++) {
            int hi = pow10(k) - 1;
            prefix[k - 1] = new IntVar(store, "prefix" + k, 0, hi);
            // prefix[k] = 10 * prefix[k-1] + digits[k-1]
            store.impose(new LinearInt(
                new IntVar[]{prefix[k - 2], digits[k - 1], prefix[k - 1]},
                new int[]{10, 1, -1}, "==", 0));
        }

        // Divisibility of the k-digit prefix by k, for k = 2..9: prefix[k] = k * quotient.
        // A 1-digit prefix is divisible by 1 whatever the digit.
        for (int k = 2; k <= 9; k++) {
            IntVar quotient = new IntVar(store, "q" + k, 0, (pow10(k) - 1) / k);
            store.impose(new XmulCeqZ(quotient, k, prefix[k - 1]));
        }

        // The whole 10-digit number is divisible by 10: its last digit is 0.
        store.impose(new XeqC(digits[9], 0));

        return new Model().putDigits("number", digits, 10).search(digits, null, null);
    }

    private static int pow10(int k) {
        int r = 1;
        for (int i = 0; i < k; i++) r *= 10;
        return r;
    }
}
