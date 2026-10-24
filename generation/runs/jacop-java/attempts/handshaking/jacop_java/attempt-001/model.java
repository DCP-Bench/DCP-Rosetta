// Handshaking (Halmos): Hilary and Jocelyn are a married couple. They invite num_couples couples.
// People: index 0 = Hilary, index 1 = Jocelyn, and the couples are (2k, 2k+1); spouse = index XOR 1.
// Nobody shakes hands with himself/herself or with his/her spouse. Jocelyn asks everyone except
// herself how many hands they shook, and all those answers are different. Output: Hilary's count.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.SumInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int c = inst.getInt("num_couples");   // invited couples, from the instance
        int people = 2 * (c + 1);             // the host couple plus the invited couples

        // Handshake matrix: h[i][j] = 1 if person i shook hands with person j.
        // It is symmetric; the diagonal and the spouse pairs are fixed to 0.
        IntVar zero = new IntVar(store, 0, 0);
        IntVar[][] h = new IntVar[people][people];
        for (int i = 0; i < people; i++)
            h[i][i] = zero;
        for (int i = 0; i < people; i++)
            for (int j = i + 1; j < people; j++) {
                if (j == (i ^ 1))             // spouses never shake hands
                    h[i][j] = zero;
                else
                    h[i][j] = new BooleanVar(store, "h" + i + "_" + j);
                h[j][i] = h[i][j];
            }

        // deg[i] = number of hands person i shook
        IntVar[] deg = new IntVar[people];
        for (int i = 0; i < people; i++) {
            deg[i] = new IntVar(store, "deg" + i, 0, people - 1);
            store.impose(new SumInt(h[i], "==", deg[i]));
        }

        // All answers are different. Jocelyn (index 1) is the one asking, so her own count
        // is left out of the distinctness requirement.
        IntVar[] answers = new IntVar[people - 1];
        int k = 0;
        for (int i = 0; i < people; i++)
            if (i != 1)
                answers[k++] = deg[i];
        store.impose(new Alldifferent(answers));

        // Label the degrees first: they decide the handshake matrix, and the all-different on them
        // prunes the rest. The matrix variables are labelled after them.
        return new Model().put("hil", deg[0]).search(deg, null, null);
    }
}
