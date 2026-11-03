// Travelling salesman: a tour that visits every city exactly once and returns to the start,
// with the shortest total length. Distance between two cities is the Euclidean distance
// between their points, rounded to an integer; the tour length is the sum of those
// rounded distances over the tour's edges.
import org.jacop.constraints.*;
import org.jacop.core.*;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // the cities come from the instance; n is the number of locations in it
        JSONArray locations = inst.getJSONArray("locations");
        int n = locations.length();

        // rounded Euclidean distance between every pair of cities
        int[][] dist = new int[n][n];
        int maxDist = 0;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                long dx = locations.getJSONArray(i).getLong(0) - locations.getJSONArray(j).getLong(0);
                long dy = locations.getJSONArray(i).getLong(1) - locations.getJSONArray(j).getLong(1);
                dist[i][j] = (int) Math.round(Math.sqrt((double) (dx * dx + dy * dy)));
                maxDist = Math.max(maxDist, dist[i][j]);
            }
        }

        // next[i] is the city visited right after city i+1 (cities are numbered 1..n)
        // Circuit needs its values 1-based: the tour is one cycle through all n cities
        IntVar[] next = new IntVar[n];
        for (int i = 0; i < n; i++) {
            next[i] = new IntVar(store, "next" + (i + 1), 1, n);
        }
        store.impose(new Circuit(next));

        // cost[i]: distance from city i+1 to the city that follows it on the tour
        // Element indexes the row with next[i] directly (offset -1), so the row is padded
        // at index 0 and holds the distance to city k at index k
        IntVar[] cost = new IntVar[n];
        for (int i = 0; i < n; i++) {
            int[] row = new int[n + 1];
            for (int k = 1; k <= n; k++) {
                row[k] = dist[i][k - 1];
            }
            cost[i] = new IntVar(store, "cost" + (i + 1), 0, maxDist);
            store.impose(Element.choose(next[i], row, cost[i], -1));
        }

        // the tour length is the sum of the edge distances
        IntVar total = new IntVar(store, "total", 0, n * maxDist);
        store.impose(new SumInt(cost, "==", total));

        Model m = new Model().put("travel_distance", total).minimize(total);
        // label the successor array first; the edge costs and the total follow from it
        m.search(next, null, null);
        return m;
    }
}
