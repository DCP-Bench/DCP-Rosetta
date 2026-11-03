// Five statements, statement i (0-based) says "exactly (i+1) of these statements are false".
// Decide which statements are true. Output: statements[i] = 1 if statement i is true, else 0.

import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // The problem fixes five statements (a problem constant, not instance data).
        int numStatements = 5;

        // statements[i] = 1 when statement i is true.
        BooleanVar[] statements = new BooleanVar[numStatements];
        for (int i = 0; i < numStatements; i++) {
            statements[i] = new BooleanVar(store, "statement" + i);
        }

        // falseCount = number of false statements = 5 - (number of true statements).
        IntVar falseCount = new IntVar(store, "falseCount", 0, numStatements);
        IntVar[] allAndFalse = new IntVar[numStatements + 1];
        int[] ones = new int[numStatements + 1];
        for (int i = 0; i < numStatements; i++) {
            allAndFalse[i] = statements[i];
            ones[i] = 1;
        }
        allAndFalse[numStatements] = falseCount;
        ones[numStatements] = 1;
        store.impose(new LinearInt(allAndFalse, ones, "==", numStatements));

        // Statement i is true exactly when the number of false statements equals i+1.
        for (int i = 0; i < numStatements; i++) {
            store.impose(new Reified(new XeqC(falseCount, i + 1), statements[i]));
        }

        return new Model().put("statements", statements);
    }
}
