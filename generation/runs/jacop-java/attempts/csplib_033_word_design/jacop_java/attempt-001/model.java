// Word design (CSPLib 033, DNA word design): find num_words words of length n
// over the alphabet {A, C, G, T}, coded 1, 2, 3, 4.
//
// Variables: words[w][k] in 1..4 is letter k of word w. Letter values follow the
// output convention: 1 = A, 2 = C, 3 = G, 4 = T.
//
// Constraints, in the problem's own terms:
//   - each word has exactly 4 symbols from {C, G} (the letters 2 and 3);
//     isCG[w][k] is 1 when that letter is C or G (a Table ties the two);
//   - each pair of distinct words differs in at least 4 positions: the number
//     of positions where they differ is at least 4;
//   - for every ordered pair (x, y), where x and y may be the same word, the
//     reverse of x and the Watson-Crick complement of y differ in at least 4
//     positions. Complement of a letter v is 5 - v (A<->T is 1<->4, C<->G is 2<->3).
//
// Sizes come from the instance: num_words words of length n. Nothing here
// depends on the example.

import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XneqY;
import org.jacop.constraints.XplusYeqC;
import org.jacop.constraints.table.Table;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        int numWords = inst.getInt("num_words");

        // Letters of each word.
        IntVar[][] words = new IntVar[numWords][n];
        // isCG[w][k] = 1 if letter k of word w is C or G.
        BooleanVar[][] isCG = new BooleanVar[numWords][n];
        // comp[w][k] = Watson-Crick complement of letter k of word w, i.e. 5 - letter.
        IntVar[][] comp = new IntVar[numWords][n];

        // Allowed (letter, isCG) pairs: A=1 -> 0, C=2 -> 1, G=3 -> 1, T=4 -> 0.
        int[][] letterCG = {{1, 0}, {2, 1}, {3, 1}, {4, 0}};

        for (int w = 0; w < numWords; w++) {
            for (int k = 0; k < n; k++) {
                words[w][k] = new IntVar(store, "w_" + w + "_" + k, 1, 4);
                isCG[w][k] = new BooleanVar(store);
                comp[w][k] = new IntVar(store, 1, 4);
                store.impose(new Table(new IntVar[]{words[w][k], isCG[w][k]}, letterCG));
                store.impose(new XplusYeqC(words[w][k], comp[w][k], 5));
            }
            // Each word has exactly 4 symbols from {C, G}.
            int[] ones = new int[n];
            java.util.Arrays.fill(ones, 1);
            store.impose(new LinearInt(isCG[w], ones, "==", 4));
        }

        // Distinct words differ in at least 4 positions.
        for (int a = 0; a < numWords; a++) {
            for (int b = a + 1; b < numWords; b++) {
                IntVar[] differ = new IntVar[n];
                int[] ones = new int[n];
                for (int k = 0; k < n; k++) {
                    BooleanVar d = new BooleanVar(store);
                    store.impose(new Reified(new XneqY(words[a][k], words[b][k]), d));
                    differ[k] = d;
                    ones[k] = 1;
                }
                store.impose(new LinearInt(differ, ones, ">=", 4));
            }
        }

        // For every ordered pair (x, y), x may equal y: reverse(x) and complement(y)
        // differ in at least 4 positions. reverse(x)[k] = x[n-1-k].
        for (int x = 0; x < numWords; x++) {
            for (int y = 0; y < numWords; y++) {
                IntVar[] differ = new IntVar[n];
                int[] ones = new int[n];
                for (int k = 0; k < n; k++) {
                    BooleanVar d = new BooleanVar(store);
                    store.impose(new Reified(
                        new XneqY(words[x][n - 1 - k], comp[y][k]), d));
                    differ[k] = d;
                    ones[k] = 1;
                }
                store.impose(new LinearInt(differ, ones, ">=", 4));
            }
        }

        Model m = new Model().put("words", words);
        return m;
    }
}
