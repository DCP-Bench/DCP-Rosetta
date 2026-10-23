// CMO 2012: given a minimum min_a and an upper bound max_val, find positive
// integers a and b with a - b = p prime and a * b = n * n (a perfect square),
// with a >= min_a, and minimise a. Outputs a, b, n and p = a - b.
import org.jacop.constraints.XmulYeqZ;
import org.jacop.constraints.XplusYeqZ;
import org.jacop.constraints.table.Table;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // the instance gives the minimum for a and the upper bound on the values
        int minA = inst.getInt("min_a");
        int maxVal = inst.getInt("max_val");

        // a is at least min_a and at most max_val; b is positive and at most max_val
        IntVar a = new IntVar(store, "a", Math.min(minA, maxVal), maxVal);
        IntVar b = new IntVar(store, "b", 1, maxVal);
        // n is the square root of a * b, so n is at most max_val
        IntVar n = new IntVar(store, "n", 1, maxVal);
        // p = a - b is a difference of two values up to max_val; a prime is at least 2
        IntVar p = new IntVar(store, "p", 2, maxVal);
        // the product a * b, bounded by max_val squared
        long sqMax = (long) maxVal * (long) maxVal;
        IntVar sq = new IntVar(store, "sq", 1, (int) Math.min(Integer.MAX_VALUE, sqMax));

        // p = a - b, that is a = b + p
        store.impose(new XplusYeqZ(b, p, a));
        // a * b is a perfect square n * n
        store.impose(new XmulYeqZ(a, b, sq));
        store.impose(new XmulYeqZ(n, n, sq));

        // p must be prime: allowed values of p are the primes up to max_val
        boolean[] composite = new boolean[maxVal + 1];
        int primeCount = 0;
        for (int v = 2; v <= maxVal; v++) {
            if (!composite[v]) {
                primeCount++;
                for (long w = (long) v * v; w <= maxVal; w += v) {
                    composite[(int) w] = true;
                }
            }
        }
        int[][] primes = new int[primeCount][1];
        int k = 0;
        for (int v = 2; v <= maxVal; v++) {
            if (!composite[v]) {
                primes[k++][0] = v;
            }
        }
        store.impose(new Table(new IntVar[]{p}, primes));

        // a is the value to minimise
        Model m = new Model().put("a", a).put("b", b).put("n", n).put("p", p);
        return m.minimize(a);
    }
}
