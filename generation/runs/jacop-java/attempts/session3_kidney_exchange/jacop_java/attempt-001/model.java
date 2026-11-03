// Kidney exchange: choose which compatible donations go ahead so that the number of
// people who receive a kidney is as large as possible. Anyone who donates must also
// receive a kidney, and no person gives or receives more than one kidney. Such
// solutions are disjoint cycles of donations.
import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("num_people");
        JSONArray compatible = inst.getJSONArray("compatible");

        // allowed[i][j] = true if person i can donate to person j
        // (the instance lists donation targets 1-based; here they are 0-based)
        boolean[][] allowed = new boolean[n][n];
        for (int i = 0; i < n; i++) {
            JSONArray row = compatible.getJSONArray(i);
            for (int k = 0; k < row.length(); k++) {
                int j = row.getInt(k) - 1;
                if (j != i) {
                    allowed[i][j] = true;
                }
            }
        }

        // transplants[i][j] = 1 if person i donates a kidney to person j
        IntVar[][] transplants = new IntVar[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (allowed[i][j]) {
                    transplants[i][j] = new BooleanVar(store, "t_" + i + "_" + j);
                } else {
                    // not a compatible pair, or a person giving to themselves: fixed to 0
                    transplants[i][j] = new IntVar(store, "t_" + i + "_" + j, 0, 0);
                }
            }
        }

        int[] unit = new int[n];
        for (int k = 0; k < n; k++) {
            unit[k] = 1;
        }

        for (int i = 0; i < n; i++) {
            // person i gives at most one kidney: sum over j of transplants[i][j] <= 1
            store.impose(new LinearInt(transplants[i], unit, "<=", 1));

            // person i receives at most one kidney: sum over j of transplants[j][i] <= 1
            IntVar[] received = new IntVar[n];
            for (int j = 0; j < n; j++) {
                received[j] = transplants[j][i];
            }
            store.impose(new LinearInt(received, unit, "<=", 1));

            // anyone who gives must receive: the number of gifts from i equals the number
            // of gifts to i (both are 0 or 1 by the two constraints above)
            // the diagonal entry transplants[i][i] is both a gift from i and a gift to i,
            // so it is left out here: it is fixed to 0 anyway
            IntVar[] balance = new IntVar[2 * (n - 1)];
            int[] balanceWeights = new int[2 * (n - 1)];
            int k = 0;
            for (int j = 0; j < n; j++) {
                if (j == i) {
                    continue;
                }
                balance[k] = transplants[i][j];
                balanceWeights[k] = 1;
                balance[(n - 1) + k] = transplants[j][i];
                balanceWeights[(n - 1) + k] = -1;
                k++;
            }
            store.impose(new LinearInt(balance, balanceWeights, "==", 0));
        }

        // objective: the number of transplants, which is the number of people receiving a kidney
        IntVar total = new IntVar(store, "total", 0, n);
        IntVar[] all = new IntVar[n * n + 1];
        int[] allWeights = new int[n * n + 1];
        IntVar[] decisions = new IntVar[n * n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                all[i * n + j] = transplants[i][j];
                allWeights[i * n + j] = 1;
                decisions[i * n + j] = transplants[i][j];
            }
        }
        all[n * n] = total;
        allWeights[n * n] = -1;
        store.impose(new LinearInt(all, allWeights, "==", 0));

        // label the transplant decisions first, the total follows from them
        Model model = new Model().put("transplants", transplants);
        return model.search(decisions, null, null).maximize(total);
    }
}
