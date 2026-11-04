// Schur's lemma: put the balls 1..n into c boxes so that no triple of balls
// (x, y, z) with x + y = z lies entirely in one box. x and y may be equal.
// balls[i] = box of ball i+1 (values 1..c).
// M[i][j] is a Boolean that is true when ball i+1 is in box j+1.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // number of balls and boxes, from the instance
        int n = inst.getInt("n");
        int c = inst.getInt("c");

        // the box of each ball, 1..c
        IntVar[] balls = new IntVar[n];
        for (int i = 0; i < n; i++) {
            balls[i] = new IntVar(store, "ball" + (i + 1), 1, c);
        }

        // M[i][j] is true exactly when ball i+1 is in box j+1
        BooleanVar[][] m = new BooleanVar[n][c];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < c; j++) {
                m[i][j] = new BooleanVar(store, "m" + (i + 1) + "_" + (j + 1));
                store.impose(new Reified(new XeqC(balls[i], j + 1), m[i][j]));
            }
        }

        // for each triple x + y = z (x <= y) and each box j, the three balls are
        // not all in box j: M[x][j] + M[y][j] + M[z][j] <= 2.
        // When x = y the ball appears twice, so its weight is 2.
        for (int x = 1; x <= n; x++) {
            for (int y = x; x + y <= n; y++) {
                int z = x + y;
                for (int j = 0; j < c; j++) {
                    IntVar[] vars;
                    int[] weights;
                    if (x == y) {
                        vars = new IntVar[]{m[x - 1][j], m[z - 1][j]};
                        weights = new int[]{2, 1};
                    } else {
                        vars = new IntVar[]{m[x - 1][j], m[y - 1][j], m[z - 1][j]};
                        weights = new int[]{1, 1, 1};
                    }
                    store.impose(new LinearInt(vars, weights, "<=", 2));
                }
            }
        }

        // a satisfaction problem: report the box of each ball
        return new Model().put("balls", balls);
    }
}
