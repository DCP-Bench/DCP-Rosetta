// Ages of the three sons. The product of the ages is 36. The sum of the ages is the number of
// windows, and the first answer "I need more information" means the sum is shared by at least two
// possible age triples. "The oldest son has blue eyes. I got it" means the oldest is unique, so every
// other triple with the same sum must have a tie for oldest. Outputs A1 >= A2 >= A3, oldest first.
//
// Candidates are the triples of positive ages, sorted oldest first, with product 36. The solver picks
// one candidate idx and states the two clues over it. No answer is written into the model.
import org.jacop.constraints.Element;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XneqY;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;
import java.util.ArrayList;
import java.util.List;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Enumerate every sorted triple a >= b >= c >= 1 with a*b*c = 36 (the first clue).
        List<int[]> cands = new ArrayList<>();
        for (int a = 1; a <= 36; a++) {
            for (int b = 1; b <= a; b++) {
                for (int c = 1; c <= b; c++) {
                    if (a * b * c == 36) {
                        cands.add(new int[]{a, b, c});
                    }
                }
            }
        }
        int k = cands.size();
        int[] age1 = new int[k];
        int[] age2 = new int[k];
        int[] age3 = new int[k];
        int[] sums = new int[k];
        boolean[] tie = new boolean[k]; // the oldest two share an age, so the oldest is not unique
        for (int j = 0; j < k; j++) {
            int[] t = cands.get(j);
            age1[j] = t[0];
            age2[j] = t[1];
            age3[j] = t[2];
            sums[j] = t[0] + t[1] + t[2];
            tie[j] = t[0] == t[1];
        }

        // idx selects the true candidate; the three ages and the sum are read from it.
        IntVar idx = new IntVar(store, 0, k - 1);
        IntVar A1 = new IntVar(store, 1, 36);
        IntVar A2 = new IntVar(store, 1, 36);
        IntVar A3 = new IntVar(store, 1, 36);
        IntVar sumI = new IntVar(store, 3, 108);
        store.impose(Element.choose(idx, age1, A1, -1));
        store.impose(Element.choose(idx, age2, A2, -1));
        store.impose(Element.choose(idx, age3, A3, -1));
        store.impose(Element.choose(idx, sums, sumI, -1));

        // Clue 2: the sum does not settle the ages. Some other candidate j has the same sum.
        IntVar other = new IntVar(store, 0, k - 1);
        IntVar sumOther = new IntVar(store, 3, 108);
        store.impose(Element.choose(other, sums, sumOther, -1));
        store.impose(new LinearInt(new IntVar[]{sumOther, sumI}, new int[]{1, -1}, "==", 0));
        store.impose(new XneqY(other, idx));

        // Clue 3: the oldest is unique, so every candidate with the same sum as the true one, other
        // than the true one itself, must be a candidate with a tie for oldest. Per candidate j without
        // a tie: if the sum equals sums[j], then the true candidate is j.
        for (int j = 0; j < k; j++) {
            if (tie[j]) {
                continue;
            }
            BooleanVar sameSum = new BooleanVar(store, "sameSum_" + j);
            store.impose(new Reified(new XeqC(sumI, sums[j]), sameSum));
            BooleanVar isJ = new BooleanVar(store, "isJ_" + j);
            store.impose(new Reified(new XeqC(idx, j), isJ));
            store.impose(new LinearInt(new IntVar[]{sameSum, isJ}, new int[]{1, -1}, "<=", 0));
        }

        return new Model().put("A1", A1).put("A2", A2).put("A3", A3)
                .search(new IntVar[]{idx, other}, null, null);
    }
}
