// Movie scheduling: choose the largest set of film offers whose filming periods
// do not overlap. Each offer is an interval [first day, last day] of filming, with
// both days included, so two offers conflict when they share at least one day.
import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // one row per offer: [title, first day, last day]; the title is ignored
        JSONArray movies = inst.getJSONArray("movies");
        int n = movies.length();
        int[] first = new int[n];
        int[] last = new int[n];
        for (int i = 0; i < n; i++) {
            JSONArray row = movies.getJSONArray(i);
            first[i] = row.getInt(1);
            last[i] = row.getInt(2);
        }

        // selected_movies[i] = 1 if offer i is accepted
        BooleanVar[] selected = new BooleanVar[n];
        for (int i = 0; i < n; i++) {
            selected[i] = new BooleanVar(store, "selected_" + i);
        }

        // no two accepted offers may share a filming day:
        // two offers i and j overlap when first[i] <= last[j] and first[j] <= last[i]
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (first[i] <= last[j] && first[j] <= last[i]) {
                    store.impose(new LinearInt(
                        new IntVar[]{selected[i], selected[j]},
                        new int[]{1, 1}, "<=", 1));
                }
            }
        }

        // objective: the number of accepted offers, to be maximised
        IntVar count = new IntVar(store, "count", 0, n);
        IntVar[] terms = new IntVar[n + 1];
        int[] weights = new int[n + 1];
        for (int i = 0; i < n; i++) {
            terms[i] = selected[i];
            weights[i] = 1;
        }
        terms[n] = count;
        weights[n] = -1;
        // sum of selected offers minus count equals 0
        store.impose(new LinearInt(terms, weights, "==", 0));

        // label the decisions first; the count follows from them
        Model model = new Model().put("selected_movies", selected);
        return model.search(selected, null, null).maximize(count);
    }
}
