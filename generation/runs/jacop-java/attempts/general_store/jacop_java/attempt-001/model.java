// General store puzzle: each letter stands for a different digit, and the words above the
// line add up to ALLWOOL. The puzzle is fixed (the instance carries no data), so the words
// are written out here. Each word is a sum of its letters times powers of ten; the sixteen
// addends minus ALLWOOL must be zero.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    private static final String[] ADDENDS = {
        "CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
        "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"
    };
    private static final String TOTAL = "ALLWOOL";
    private static final String LETTERS = "ABCEHLOPSW";

    public static Model build(JSONObject inst, Store store) {
        // one variable per letter, each a digit 0..9
        IntVar[] vars = new IntVar[LETTERS.length()];
        for (int k = 0; k < LETTERS.length(); k++) {
            vars[k] = new IntVar(store, "letter_" + LETTERS.charAt(k), 0, 9);
        }

        // each different letter stands for a different digit
        store.impose(new Alldifferent(vars));

        // weight of each letter in (sum of addends) - TOTAL: a letter at position p from the
        // right counts 10^p in each word it appears in, with a minus sign for TOTAL
        int[] weight = new int[LETTERS.length()];
        for (String word : ADDENDS) {
            addWord(word, 1, weight);
        }
        addWord(TOTAL, -1, weight);

        // the column sums balance: sum of weight[k] * letter[k] == 0
        store.impose(new LinearInt(vars, weight, "==", 0));

        // label the letters
        Model model = new Model();
        for (int k = 0; k < LETTERS.length(); k++) {
            model.put(String.valueOf(LETTERS.charAt(k)), vars[k]);
        }
        return model.search(vars, null, null);
    }

    private static void addWord(String word, int sign, int[] weight) {
        long place = 1;
        for (int p = word.length() - 1; p >= 0; p--) {
            int k = LETTERS.indexOf(word.charAt(p));
            weight[k] += sign * (int) place;
            place *= 10;
        }
    }
}
