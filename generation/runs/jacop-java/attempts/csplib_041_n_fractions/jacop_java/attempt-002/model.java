// N-fractions puzzle: find distinct non-zero digits A..I such that
//     A/BC + D/EF + G/HI = 1,
// where BC, EF and HI are the two-digit numbers 10*B+C, 10*E+F and 10*H+I.
// Clearing the denominators gives an integer equation:
//     A*(EF*HI) + D*(BC*HI) + G*(BC*EF) = BC*EF*HI.
import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // The nine digits are distinct and non-zero, so they are exactly 1..9 in some order.
        IntVar A = new IntVar(store, "A", 1, 9);
        IntVar B = new IntVar(store, "B", 1, 9);
        IntVar C = new IntVar(store, "C", 1, 9);
        IntVar D = new IntVar(store, "D", 1, 9);
        IntVar E = new IntVar(store, "E", 1, 9);
        IntVar F = new IntVar(store, "F", 1, 9);
        IntVar G = new IntVar(store, "G", 1, 9);
        IntVar H = new IntVar(store, "H", 1, 9);
        IntVar I = new IntVar(store, "I", 1, 9);
        store.impose(new Alldifferent(new IntVar[]{A, B, C, D, E, F, G, H, I}));

        // Two-digit numbers: BC = 10*B + C, and likewise EF and HI.
        IntVar BC = new IntVar(store, "BC", 11, 99);
        IntVar EF = new IntVar(store, "EF", 11, 99);
        IntVar HI = new IntVar(store, "HI", 11, 99);
        store.impose(new LinearInt(new IntVar[]{B, C, BC}, new int[]{10, 1, -1}, "==", 0));
        store.impose(new LinearInt(new IntVar[]{E, F, EF}, new int[]{10, 1, -1}, "==", 0));
        store.impose(new LinearInt(new IntVar[]{H, I, HI}, new int[]{10, 1, -1}, "==", 0));

        // Products of the denominators, then the cleared equation
        // A*(EF*HI) + D*(BC*HI) + G*(BC*EF) = BC*EF*HI.
        IntVar EFHI = new IntVar(store, "EFxHI", 121, 9801);
        IntVar BCHI = new IntVar(store, "BCxHI", 121, 9801);
        IntVar BCEF = new IntVar(store, "BCxEF", 121, 9801);
        IntVar BCEFHI = new IntVar(store, "BCxEFxHI", 1331, 970299);
        store.impose(new XmulYeqZ(EF, HI, EFHI));
        store.impose(new XmulYeqZ(BC, HI, BCHI));
        store.impose(new XmulYeqZ(BC, EF, BCEF));
        store.impose(new XmulYeqZ(BC, EFHI, BCEFHI));

        IntVar t1 = new IntVar(store, "A_EFHI", 0, 9 * 9801);
        IntVar t2 = new IntVar(store, "D_BCHI", 0, 9 * 9801);
        IntVar t3 = new IntVar(store, "G_BCEF", 0, 9 * 9801);
        store.impose(new XmulYeqZ(A, EFHI, t1));
        store.impose(new XmulYeqZ(D, BCHI, t2));
        store.impose(new XmulYeqZ(G, BCEF, t3));
        store.impose(new SumInt(new IntVar[]{t1, t2, t3}, "==", BCEFHI));

        return new Model()
            .put("A", A).put("B", B).put("C", C)
            .put("D", D).put("E", E).put("F", F)
            .put("G", G).put("H", H).put("I", I);
    }
}
