// Circular table (Averbach 1-2): three players X, Y, Z of different nationalities
// (American, English, French) sit around a circular table playing Hearts. Each
// passes three cards to the person on their right. Y passes to the American, and
// X passes to the person who passes to the Frenchwoman. Find each nationality.
//
// Seats are 0, 1, 2 with 1 right of 0 and 2 right of 1 (and 0 right of 2), so the
// person on the right of seat s is (s + 1) mod 3.
import org.jacop.constraints.*;
import org.jacop.core.*;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // x, y, z: the seat of each player X, Y, Z
        IntVar x = new IntVar(store, "x", 0, 2);
        IntVar y = new IntVar(store, "y", 0, 2);
        IntVar z = new IntVar(store, "z", 0, 2);
        // american, english, french: the seat of each nationality
        IntVar american = new IntVar(store, "american", 0, 2);
        IntVar english = new IntVar(store, "english", 0, 2);
        IntVar french = new IntVar(store, "french", 0, 2);

        // the three players sit in three different seats, and so do the nationalities
        store.impose(new Alldifferent(new IntVar[]{x, y, z}));
        store.impose(new Alldifferent(new IntVar[]{american, english, french}));

        // Y passed three hearts to the American: the American sits on Y's right,
        // american = (y + 1) mod 3
        store.impose(new org.jacop.constraints.table.Table(
                new IntVar[]{y, american},
                new int[][]{{0, 1}, {1, 2}, {2, 0}}));

        // X passed to the person P who passed to the Frenchwoman. P sits on X's right,
        // and the Frenchwoman sits on P's right, so french = (x + 2) mod 3
        store.impose(new org.jacop.constraints.table.Table(
                new IntVar[]{x, french},
                new int[][]{{0, 2}, {1, 0}, {2, 1}}));

        return new Model().put("x", x).put("y", y).put("z", z)
                .put("american", american).put("english", english).put("french", french);
    }
}
