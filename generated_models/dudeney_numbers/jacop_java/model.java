// Dudeney numbers: find a positive perfect cube (larger than 1) whose digit sum
// equals the cube root of the number. Output: "number".
//
// The instance field n is the maximum number of digits, so the number is below 10^n.
// Digits are modelled explicitly: d[i] is the i-th digit (units first), 0..9.
// The cube is cube = c*c*c with c = cube root, and digit sum = c.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import org.jacop.search.IndomainMin;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        // The cube is an int variable, and the digit weights 10^i must fit in int:
        // this model supports n up to 9 digits, which covers every instance.
        if (n < 1 || n > 9) {
            throw new IllegalArgumentException("n must be between 1 and 9, got " + n);
        }

        // Upper bound on the number: 10^n - 1, so every digit string of length n is possible.
        int limit = 1;
        for (int i = 0; i < n; i++) limit *= 10;   // 10^n, fits in int for n <= 9
        int maxNumber = limit - 1;

        // Largest c with c^3 <= 10^n - 1, computed from the instance's n.
        int cMax = 1;
        while ((long) (cMax + 1) * (cMax + 1) * (cMax + 1) <= maxNumber) cMax++;

        // c is the cube root, decided first. "Larger than 1" excludes c = 1 (the number 1),
        // so c starts at 2.
        IntVar c = new IntVar(store, "c", 2, cMax);
        IntVar sq = new IntVar(store, "sq", 4, cMax * cMax);
        IntVar cube = new IntVar(store, "cube", 8, maxNumber);
        store.impose(new XmulYeqZ(c, c, sq));      // c * c = sq
        store.impose(new XmulYeqZ(sq, c, cube));   // sq * c = cube, so cube = c^3

        // The digits of the number, units first. Each digit is 0..9, and together they
        // write the cube in base 10 (so the cube is below 10^n).
        IntVar[] d = new IntVar[n];
        for (int i = 0; i < n; i++) {
            d[i] = new IntVar(store, "d" + i, 0, 9);
        }

        // Positional value: cube = sum of d[i] * 10^i.
        // Written as sum(d[i] * 10^i) - cube = 0.
        IntVar[] posVars = new IntVar[n + 1];
        int[] posW = new int[n + 1];
        int pow = 1;
        for (int i = 0; i < n; i++) {
            posVars[i] = d[i];
            posW[i] = pow;
            pow *= 10;   // stays within int: 10^(n-1) for n <= 9
        }
        posVars[n] = cube;
        posW[n] = -1;
        store.impose(new LinearInt(posVars, posW, "==", 0));

        // Digit sum equals the cube root: sum(d[i]) - c = 0.
        IntVar[] sumVars = new IntVar[n + 1];
        int[] sumW = new int[n + 1];
        for (int i = 0; i < n; i++) {
            sumVars[i] = d[i];
            sumW[i] = 1;
        }
        sumVars[n] = c;
        sumW[n] = -1;
        store.impose(new LinearInt(sumVars, sumW, "==", 0));

        // Search: label the cube root first, which fixes the cube and the digits.
        return new Model().put("number", cube).search(new IntVar[]{c}, null, new IndomainMin<>());
    }
}
