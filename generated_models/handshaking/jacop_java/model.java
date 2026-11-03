// Handshaking (Halmos): Hilary (index 0) and Jocelyn (index 1) are a couple and invite num_couples
// couples (2k, 2k+1). Nobody shakes hands with self or spouse (spouse = index XOR 1). Jocelyn asks
// everyone but herself how many hands they shook; all answers differ. Output: Hilary's count.
// Implied facts added for propagation: the n-1 distinct answers lie in 0..n-2, so they are exactly
// 0..n-2 (fixed sum); the two spouses of an invited couple always add up to n-2.
// Symmetry breaking (allowed: the output only has to extend to a solution): inside each invited couple
// the degrees are ordered, and the couples are ordered by their first member.
import org.jacop.constraints.*;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int c = inst.getInt("num_couples");
        int n = 2 * (c + 1);                  // people

        // one 0/1 variable per non-spouse pair, shared by both directions
        BooleanVar[][] h = new BooleanVar[n][n];
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++)
                if (j != (i ^ 1)) {
                    h[i][j] = new BooleanVar(store, "h" + i + "_" + j);
                    h[j][i] = h[i][j];
                }

        // deg[i] = sum of row i; max degree is n-2 (not self, not spouse)
        IntVar[] deg = new IntVar[n];
        for (int i = 0; i < n; i++) {
            deg[i] = new IntVar(store, "deg" + i, 0, n - 2);
            IntVar[] row = new IntVar[n - 2 + 1];
            int[] w = new int[n - 2 + 1];
            int k = 0;
            for (int j = 0; j < n; j++)
                if (j != i && j != (i ^ 1)) { row[k] = h[i][j]; w[k++] = 1; }
            row[k] = deg[i]; w[k] = -1;
            store.impose(new LinearInt(row, w, "==", 0));
        }

        // everyone but Jocelyn gives a different answer
        IntVar[] answers = new IntVar[n - 1];
        int k = 0;
        for (int i = 0; i < n; i++) if (i != 1) answers[k++] = deg[i];
        store.impose(new Alldifferent(answers));
        // implied: they are exactly 0..n-2
        int[] ones = new int[n - 1];
        java.util.Arrays.fill(ones, 1);
        store.impose(new LinearInt(answers, ones, "==", (n - 2) * (n - 1) / 2));

        // implied: spouses of an invited couple sum to n-2; order within and between couples
        for (int p = 1; p <= c; p++) {
            IntVar a = deg[2 * p], b = deg[2 * p + 1];
            store.impose(new LinearInt(new IntVar[]{a, b}, new int[]{1, 1}, "==", n - 2));
            store.impose(new XltY(a, b));
            if (p > 1) store.impose(new XltY(deg[2 * (p - 1)], a));
        }

        return new Model().put("hil", deg[0]).search(deg, new org.jacop.search.SmallestDomain<IntVar>(), null);
    }
}
