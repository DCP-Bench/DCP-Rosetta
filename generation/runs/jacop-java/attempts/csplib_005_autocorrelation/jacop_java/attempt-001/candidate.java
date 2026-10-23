// Low autocorrelation binary sequences (CSPLib 005), periodic boundary conditions:
// choose a sequence S of n bits, each +1 or -1, that minimises the energy
// E = sum over k = 1..n-1 of C_k^2, where C_k = sum over i of S_i * S_((i+k) mod n).

import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // Instance data: n, the length of the sequence.
        int n = inst.getInt("n");

        // bit[i] = 1 encodes S_i = +1 and bit[i] = 0 encodes S_i = -1.
        // The output sequence S_i (value -1 or +1) is linked to bit[i] by
        // S_i = 2*bit[i] - 1, so S_i can never be 0.
        BooleanVar[] bit = new BooleanVar[n];
        IntVar[] s = new IntVar[n];
        for (int i = 0; i < n; i++) {
            bit[i] = new BooleanVar(store, "bit_" + i);
            s[i] = new IntVar(store, "S_" + i, -1, 1);
            IntVar[] link = {s[i], bit[i]};
            int[] linkWeights = {1, -2};
            store.impose(new LinearInt(link, linkWeights, "==", -1));
        }

        // Periodic autocorrelation C_k for k = 1..n-1, and its square.
        // The product of two bits, p, is the term S_i * S_((i+k) mod n); it is
        // +1 or -1 because neither factor is 0.
        IntVar[] squares = new IntVar[Math.max(n - 1, 0)];
        for (int k = 1; k < n; k++) {
            IntVar[] terms = new IntVar[n];
            int[] ones = new int[n];
            for (int i = 0; i < n; i++) {
                int j = (i + k) % n;
                IntVar p = new IntVar(store, "p_" + k + "_" + i, -1, 1);
                store.impose(new XmulYeqZ(s[i], s[j], p));
                terms[i] = p;
                ones[i] = 1;
            }

            // C_k = sum of the n terms; the bounds on C_k follow from n.
            IntVar c = new IntVar(store, "C_" + k, -n, n);
            IntVar[] cVars = new IntVar[n + 1];
            int[] cWeights = new int[n + 1];
            for (int i = 0; i < n; i++) {
                cVars[i] = terms[i];
                cWeights[i] = 1;
            }
            cVars[n] = c;
            cWeights[n] = -1;
            store.impose(new LinearInt(cVars, cWeights, "==", 0));

            // C_k squared, one term of the energy.
            IntVar sq = new IntVar(store, "sq_" + k, 0, n * n);
            store.impose(new XmulYeqZ(c, c, sq));
            squares[k - 1] = sq;
        }

        // Energy E = sum of the squared autocorrelations: the objective.
        int energyMax = Math.max(n - 1, 0) * n * n;
        IntVar energy = new IntVar(store, "energy", 0, energyMax);
        IntVar[] eVars = new IntVar[squares.length + 1];
        int[] eWeights = new int[squares.length + 1];
        for (int k = 0; k < squares.length; k++) {
            eVars[k] = squares[k];
            eWeights[k] = 1;
        }
        eVars[squares.length] = energy;
        eWeights[squares.length] = -1;
        store.impose(new LinearInt(eVars, eWeights, "==", 0));

        // Labels the bit decisions first; the sequence values and autocorrelations follow.
        return new Model()
                .put("sequence", s)
                .search(bit, null, null)
                .minimize(energy);
    }
}
