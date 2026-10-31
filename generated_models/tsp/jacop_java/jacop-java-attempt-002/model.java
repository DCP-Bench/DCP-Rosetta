// Travelling salesman: a tour that visits every city exactly once and returns to the start,
// with the shortest total length. Distance between two cities is the Euclidean distance
// between their points, rounded to an integer; the tour length is the sum of those
// rounded distances over the tour's edges.
import java.util.*;
import org.jacop.constraints.*;
import org.jacop.core.*;
import org.jacop.search.*;
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

        // Rank encoding. rank[i] says which of city i's other cities (sorted by distance,
        // nearest first) is the successor. Labelling rank with IndomainMin therefore tries
        // the nearest successor first, which finds short tours early and prunes the bound.
        // nbr[i][k] is the (1-based) city at position k in city i's distance order and
        // sd[i][k] its distance, so the cost is non-decreasing in the rank.
        int m1 = n - 1;
        IntVar[] rank = new IntVar[n];
        IntVar[] next = new IntVar[n];
        IntVar[] cost = new IntVar[n];
        for (int i = 0; i < n; i++) {
            final int ci = i;
            Integer[] order = new Integer[m1];
            int p = 0;
            for (int j = 0; j < n; j++) if (j != i) order[p++] = j;
            Arrays.sort(order, (a, b) -> dist[ci][a] != dist[ci][b]
                    ? Integer.compare(dist[ci][a], dist[ci][b]) : Integer.compare(a, b));
            int[] nbr = new int[m1];
            int[] sd = new int[m1];
            for (int k = 0; k < m1; k++) { nbr[k] = order[k] + 1; sd[k] = dist[i][order[k]]; }

            rank[i] = new IntVar(store, "rank" + (i + 1), 0, m1 - 1);
            next[i] = new IntVar(store, "next" + (i + 1), 1, n);
            cost[i] = new IntVar(store, "cost" + (i + 1), sd[0], sd[m1 - 1]);
            // Element is 0-based here with offset -1: array[rank] = value
            store.impose(Element.choose(rank[i], nbr, next[i], -1));
            store.impose(Element.choose(rank[i], sd, cost[i], -1));
        }

        // the successors form one cycle through all n cities (values are 1-based)
        store.impose(new Circuit(next));
        // redundant: every city has exactly one predecessor (stronger pruning on next)
        store.impose(new Alldifferent(next));

        // the tour length is the sum of the edge distances
        IntVar total = new IntVar(store, "total", 0, n * maxDist);
        store.impose(new SumInt(cost, "==", total));

        Model m = new Model().put("travel_distance", total).minimize(total);
        // label the ranks first (nearest successor first); the rest follows by propagation
        m.search(rank, new SmallestDomain<IntVar>(), new IndomainMin<IntVar>());
        return m;
    }
}
