// Crypta: a cryptarithm. Assign a distinct digit 0..9 to each letter A..J so that
// AUGEND + ADDEND = SUM holds as 20-digit decimal numbers, with no leading zero.
import java.util.LinkedHashMap;
import java.util.Map;
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {

    // Problem constants from the statement, not from the instance. Each word is 20 letters,
    // most significant first.
    static final String AUGEND = "BAIJJAJIIAHFCFEBBJEA";
    static final String ADDEND = "DHFGABCDIDBIFFAGFEJE";
    static final String SUM    = "GJEGACDDHFAFJBFIHEEF";
    static final String LETTERS = "ABCDEFGHIJ";

    public static Model build(JSONObject instance, Store store) {
        int n = AUGEND.length();

        // One digit variable per letter. The first letter of each number is not zero.
        IntVar[] L = new IntVar[LETTERS.length()];
        for (int i = 0; i < L.length; i++) {
            char ch = LETTERS.charAt(i);
            boolean leading = ch == AUGEND.charAt(0) || ch == ADDEND.charAt(0) || ch == SUM.charAt(0);
            L[i] = new IntVar(store, String.valueOf(ch), leading ? 1 : 0, 9);
        }

        // All letters stand for different digits.
        store.impose(new Alldifferent(L));

        // Column addition, column 0 at the right. carry[k] is the carry into column k.
        // The carries into column 0 and out of the last column are zero.
        IntVar[] carry = new IntVar[n + 1];
        for (int k = 0; k <= n; k++)
            carry[k] = (k == 0 || k == n) ? new IntVar(store, 0, 0) : new IntVar(store, "carry" + k, 0, 1);

        for (int k = 0; k < n; k++) {
            int p = n - 1 - k;   // position of this column in the words, counted from the left
            // Column k: augend digit + addend digit + carry in = sum digit + 10 * carry out.
            Map<IntVar, Integer> terms = new LinkedHashMap<>();   // merges a letter used twice
            add(terms, L[LETTERS.indexOf(AUGEND.charAt(p))], 1);
            add(terms, L[LETTERS.indexOf(ADDEND.charAt(p))], 1);
            add(terms, L[LETTERS.indexOf(SUM.charAt(p))], -1);
            add(terms, carry[k], 1);
            add(terms, carry[k + 1], -10);

            IntVar[] xs = new IntVar[terms.size()];
            int[] ws = new int[terms.size()];
            int i = 0;
            for (Map.Entry<IntVar, Integer> e : terms.entrySet()) {
                xs[i] = e.getKey();
                ws[i] = e.getValue();
                i++;
            }
            store.impose(new LinearInt(xs, ws, "==", 0));
        }

        // Output: the digit of each letter, A..J.
        Model m = new Model();
        for (int i = 0; i < L.length; i++) m = m.put(String.valueOf(LETTERS.charAt(i)), L[i]);

        // Label the letters first; the carries follow from them.
        return m.search(L, null, null);
    }

    static void add(Map<IntVar, Integer> terms, IntVar x, int w) {
        terms.merge(x, w, Integer::sum);
    }
}
