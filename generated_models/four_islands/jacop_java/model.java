// Four islands: find the name, export and tourist attraction of each of four islands.
// Map positions: A=0 (north-west), B=1 (north-east), C=2 (south-west), D=3 (south-east).
// Bridges join A-B, A-C, B-D and C-D. Each island, export and attraction is a permutation of 0..3.
//
// island[i]      = map position of island i (Pwana, Quero, Rayou, Skern)
// export[j]      = map position of the island exporting j (alabaster, bananas, coconuts, durian fruit)
// attraction[j]  = map position of the island with attraction j (hotel, ice rink, jai alai, koala)
//
// Each clue is a Table over the two positions it relates, listing the allowed (first, second) pairs.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.table.Table;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {

    // (north, south) pairs in the same column: A is due north of C, B is due north of D.
    static final int[][] NORTH_SOUTH_BELOW = {{0, 2}, {1, 3}};
    // (west, east) pairs in the same row: A is due west of B, C is due west of D.
    static final int[][] WEST_EAST = {{0, 1}, {2, 3}};
    // Adjacent by a north-south bridge (A-C, B-D), in either order.
    static final int[][] NS_BRIDGE = {{0, 2}, {2, 0}, {1, 3}, {3, 1}};
    // Adjacent by an east-west bridge (A-B, C-D), in either order.
    static final int[][] EW_BRIDGE = {{0, 1}, {1, 0}, {2, 3}, {3, 2}};
    // Not connected by any bridge and distinct: the diagonals A-D and B-C, in either order.
    static final int[][] NOT_BRIDGED = {{0, 3}, {3, 0}, {1, 2}, {2, 1}};

    public static Model build(JSONObject instance, Store store) {
        // Islands: 0 Pwana, 1 Quero, 2 Rayou, 3 Skern.
        IntVar[] island = new IntVar[4];
        // Exports: 0 alabaster, 1 bananas, 2 coconuts, 3 durian fruit.
        IntVar[] export = new IntVar[4];
        // Attractions: 0 resort hotel, 1 ice skating rink, 2 jai alai stadium, 3 koala preserve.
        IntVar[] attraction = new IntVar[4];
        for (int i = 0; i < 4; i++) {
            island[i] = new IntVar(store, "island" + i, 0, 3);
            export[i] = new IntVar(store, "export" + i, 0, 3);
            attraction[i] = new IntVar(store, "attraction" + i, 0, 3);
        }
        store.impose(new Alldifferent(island));
        store.impose(new Alldifferent(export));
        store.impose(new Alldifferent(attraction));

        // 1. The koala preserve island is due south of Pwana.
        store.impose(new Table(new IntVar[]{island[0], attraction[3]}, NORTH_SOUTH_BELOW));
        // 2. The alabaster island is due west of Quero.
        store.impose(new Table(new IntVar[]{export[0], island[1]}, WEST_EAST));
        // 3. The resort hotel island is due east of the durian fruit exporter.
        store.impose(new Table(new IntVar[]{export[3], attraction[0]}, WEST_EAST));
        // 4. Skern and the jai alai stadium island are connected by a north-south bridge.
        store.impose(new Table(new IntVar[]{island[3], attraction[2]}, NS_BRIDGE));
        // 5. Rayou and the banana exporter are connected by an east-west bridge.
        store.impose(new Table(new IntVar[]{island[2], export[1]}, EW_BRIDGE));
        // 6. The ice skating rink island and the jai alai stadium island are not connected by a bridge.
        store.impose(new Table(new IntVar[]{attraction[1], attraction[2]}, NOT_BRIDGED));

        Model model = new Model()
            .put("island", island)
            .put("export", export)
            .put("attraction", attraction);
        return model;
    }
}
