// Circling the squares: ten different whole numbers are placed on a circle in the
// order A, B, C, D, E, F, G, H, I, K. For any two adjacent numbers, the sum of
// their squares equals the sum of the squares of the two numbers diametrically
// opposite them. Fill in the ten numbers given A=16, B=2, F=8, G=14.
import org.jacop.constraints.*;
import org.jacop.core.*;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        final int n = 10;           // ten squares around the circle
        final int maxFigures = 99;  // the statement: no number needs more than two figures

        // positions 0..9 are A, B, C, D, E, F, G, H, I, K around the circle
        String[] names = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "K"};
        IntVar[] x = new IntVar[n];
        IntVar[] sq = new IntVar[n];
        for (int i = 0; i < n; i++) {
            x[i] = new IntVar(store, names[i], 0, maxFigures);
            sq[i] = new IntVar(store, "sq" + names[i], 0, maxFigures * maxFigures);
            store.impose(new XmulYeqZ(x[i], x[i], sq[i]));  // sq = number squared
        }

        // the numbers are different from each other
        store.impose(new Alldifferent(x));

        // the four numbers given in the statement
        store.impose(new XeqC(x[0], 16));  // A
        store.impose(new XeqC(x[1], 2));   // B
        store.impose(new XeqC(x[5], 8));   // F
        store.impose(new XeqC(x[6], 14));  // G

        // for each adjacent pair (i, i+1), the squares of the pair equal the squares of
        // the diametrically opposite pair (i+5, i+6); positions wrap around the circle
        for (int i = 0; i < n; i++) {
            int a = i, b = (i + 1) % n, c = (i + 5) % n, d = (i + 6) % n;
            store.impose(new LinearInt(new IntVar[]{sq[a], sq[b], sq[c], sq[d]},
                    new int[]{1, 1, -1, -1}, "==", 0));
        }

        Model model = new Model();
        for (int i = 0; i < n; i++) {
            model.put(names[i], x[i]);
        }
        return model;
    }
}
