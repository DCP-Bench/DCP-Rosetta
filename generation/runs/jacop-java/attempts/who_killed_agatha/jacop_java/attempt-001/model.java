import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XeqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

// Three people, indexed by their position in the instance's names array.
// hates[p][q]: person p hates person q.  richer[p][q]: person p is richer than person q.
// kill[p]: person p killed Agatha. The killer's index is the output.
public class Submission {
    public static Model build(JSONObject instance, Store store) {
        JSONArray names = instance.getJSONArray("names");
        int n = names.length();

        // Find the three people by name, so the clues attach to the right index.
        int agatha = -1, butler = -1, charles = -1;
        for (int i = 0; i < n; i++) {
            String s = names.getString(i).toLowerCase();
            if (s.contains("agatha")) agatha = i;
            else if (s.contains("butler")) butler = i;
            else if (s.contains("charles")) charles = i;
        }

        BooleanVar[][] hates = new BooleanVar[n][n];
        BooleanVar[][] richer = new BooleanVar[n][n];
        for (int p = 0; p < n; p++) {
            for (int q = 0; q < n; q++) {
                hates[p][q] = new BooleanVar(store, "hates" + p + "_" + q);
                richer[p][q] = new BooleanVar(store, "richer" + p + "_" + q);
            }
        }
        BooleanVar[] kill = new BooleanVar[n];
        for (int p = 0; p < n; p++) kill[p] = new BooleanVar(store, "kill" + p);

        // Richer is irreflexive: nobody is richer than himself.
        for (int p = 0; p < n; p++) store.impose(new XeqC(richer[p][p], 0));

        // Agatha hates everybody except the butler (including herself).
        for (int q = 0; q < n; q++) {
            store.impose(new XeqC(hates[agatha][q], q == butler ? 0 : 1));
        }

        // Charles hates no one whom Agatha hates: hates[A][q] implies not hates[C][q].
        for (int q = 0; q < n; q++) {
            store.impose(new LinearInt(new IntVar[]{hates[agatha][q], hates[charles][q]},
                new int[]{1, 1}, "<=", 1));
        }

        // The butler hates everyone whom Agatha hates: hates[A][q] implies hates[B][q].
        for (int q = 0; q < n; q++) {
            store.impose(new LinearInt(new IntVar[]{hates[agatha][q], hates[butler][q]},
                new int[]{1, -1}, "<=", 0));
        }

        // The butler hates everyone not richer than Agatha: not richer[q][A] implies hates[B][q].
        for (int q = 0; q < n; q++) {
            store.impose(new LinearInt(new IntVar[]{richer[q][agatha], hates[butler][q]},
                new int[]{1, 1}, ">=", 1));
        }

        // Nobody hates everyone: each person hates at most n-1 people.
        for (int p = 0; p < n; p++) {
            store.impose(new LinearInt(hates[p], ones(n), "<=", n - 1));
        }

        // The killer is one person, hates Agatha, and is no richer than Agatha.
        store.impose(new LinearInt(kill, ones(n), "==", 1));
        for (int p = 0; p < n; p++) {
            // kill[p] implies hates[p][A]
            store.impose(new LinearInt(new IntVar[]{kill[p], hates[p][agatha]},
                new int[]{1, -1}, "<=", 0));
            // kill[p] implies not richer[p][A]
            store.impose(new LinearInt(new IntVar[]{kill[p], richer[p][agatha]},
                new int[]{1, 1}, "<=", 1));
        }

        // Output: killer = sum over p of p * kill[p], so killer - sum(p*kill[p]) = 0.
        IntVar killer = new IntVar(store, "killer", 0, n - 1);
        IntVar[] terms = new IntVar[n + 1];
        int[] weights = new int[n + 1];
        for (int p = 0; p < n; p++) {
            terms[p] = kill[p];
            weights[p] = p;
        }
        terms[n] = killer;
        weights[n] = -1;
        store.impose(new LinearInt(terms, weights, "==", 0));

        return new Model().put("killer", killer);
    }

    static int[] ones(int n) {
        int[] w = new int[n];
        java.util.Arrays.fill(w, 1);
        return w;
    }
}
