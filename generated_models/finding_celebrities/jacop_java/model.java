// Finding celebrities: guest i is a celebrity when every other guest knows i, and i knows only other
// celebrities. At least one celebrity is present. graph[i][j] = 1 when guest i knows guest j. The
// diagonal (a guest knowing himself) is ignored, since the problem only concerns other guests.
// Output celebrities[i] = 1 if guest i is a celebrity.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XeqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray graph = inst.getJSONArray("graph");
        int n = graph.length();

        // celeb[i] = 1 if guest i is a celebrity.
        IntVar[] celeb = new IntVar[n];
        for (int i = 0; i < n; i++) {
            celeb[i] = new BooleanVar(store, "celeb_" + i);
        }

        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (i == j) {
                    continue;
                }
                // Everybody knows a celebrity: if guest j does not know guest i, then i is not a celebrity.
                if (graph.getJSONArray(j).getInt(i) == 0) {
                    store.impose(new XeqC(celeb[i], 0));
                }
                // A celebrity knows only other celebrities: if i knows j, then celeb[i] implies celeb[j].
                if (graph.getJSONArray(i).getInt(j) != 0) {
                    store.impose(new LinearInt(new IntVar[]{celeb[i], celeb[j]}, new int[]{1, -1}, "<=", 0));
                }
            }
        }

        // At least one celebrity is present at the party.
        int[] ones = new int[n];
        java.util.Arrays.fill(ones, 1);
        store.impose(new LinearInt(celeb, ones, ">=", 1));

        // Label the celebrity flags; they are the whole output.
        return new Model().put("celebrities", celeb).search(celeb, null, null);
    }
}
