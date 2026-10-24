// Graph colouring: colour six countries (1 Belgium, 2 Denmark, 3 France, 4 Germany, 5 Netherlands,
// 6 Luxembourg) so that neighbouring countries get different colours, using as few colours as possible.
// The graph is read from the instance: each row is an edge between two countries, numbered from 1.
import org.jacop.constraints.Max;
import org.jacop.constraints.XneqY;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject instance, Store store) {
        int countries = 6;   // the problem fixes six countries
        JSONArray graph = instance.getJSONArray("graph");

        // colors[k] is the colour of country k+1; colours are 1..countries
        IntVar[] colors = new IntVar[countries];
        for (int k = 0; k < countries; k++) {
            colors[k] = new IntVar(store, "colour" + (k + 1), 1, countries);
        }

        // two neighbouring countries cannot have the same colour
        for (int e = 0; e < graph.length(); e++) {
            JSONArray edge = graph.getJSONArray(e);
            int u = edge.getInt(0) - 1;   // instance countries are numbered from 1
            int v = edge.getInt(1) - 1;
            store.impose(new XneqY(colors[u], colors[v]));
        }

        // the number of colours used is the highest colour number used
        IntVar colourCount = new IntVar(store, "coloursUsed", 1, countries);
        store.impose(new Max(colors, colourCount));

        Model model = new Model().put("colors", colors);
        return model.minimize(colourCount);
    }
}
