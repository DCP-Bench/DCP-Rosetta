// People entering a room: 13 people, 4 male and 9 female, enter one at a time. At any time the ratio of
// females to males in the room must be at most 7/3. The instance carries no data.
import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject instance, Store store) {
        int people = 13;
        int males = 4;
        int females = people - males;

        // sequence[t] = 1 if the t-th person to enter is female, 0 if male
        BooleanVar[] sequence = new BooleanVar[people];
        for (int t = 0; t < people; t++) {
            sequence[t] = new BooleanVar(store, "entry" + (t + 1));
        }

        // exactly 4 males and 9 females enter
        IntVar[] all = new IntVar[people];
        int[] ones = new int[people];
        for (int t = 0; t < people; t++) {
            all[t] = sequence[t];
            ones[t] = 1;
        }
        store.impose(new LinearInt(all, ones, "==", females));

        // after each entry, with f females and m = t - f males in the room (t people so far):
        // f / m <= 7/3, i.e. 3*f <= 7*m, i.e. 10*f <= 7*t. An empty room with a female in it breaks this,
        // so the first person to enter is male.
        for (int t = 1; t <= people; t++) {
            IntVar[] prefix = new IntVar[t];
            int[] weights = new int[t];
            for (int s = 0; s < t; s++) {
                prefix[s] = sequence[s];
                weights[s] = 10;
            }
            store.impose(new LinearInt(prefix, weights, "<=", 7 * t));
        }

        Model model = new Model().put("sequence", sequence);
        return model;
    }
}
