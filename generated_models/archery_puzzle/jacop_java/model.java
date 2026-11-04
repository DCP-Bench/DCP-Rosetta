// Archery: the archer shoots as many arrows as she likes at each target ring.
// hits[k] is the number of arrows landing on ring k, and ring k scores targets[k]
// per arrow. Minimise how far the total score is from target_score, in either
// direction (the deviation |total - target_score|).
import org.jacop.constraints.AbsXeqY;
import org.jacop.constraints.LinearInt;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        JSONArray targets = inst.getJSONArray("targets");
        int target = inst.getInt("target_score");
        int n = targets.length();

        int maxRing = 0;
        for (int k = 0; k < n; k++) {
            maxRing = Math.max(maxRing, targets.getInt(k));
        }

        // Bound on arrows per ring: in an optimal shot, hits[k] * targets[k] <=
        // target + maxRing, because one more arrow beyond that would make the
        // total at least target and strictly reduce the deviation.
        IntVar[] hits = new IntVar[n];
        IntVar[] sumVars = new IntVar[n + 1];
        int[] sumWeights = new int[n + 1];
        int totalMax = 0;
        for (int k = 0; k < n; k++) {
            int ring = targets.getInt(k);
            int maxHits = (target + maxRing) / ring;
            hits[k] = new IntVar(store, "hits" + k, 0, maxHits);
            sumVars[k] = hits[k];
            sumWeights[k] = ring;
            totalMax += maxHits * ring;
        }

        // total = sum of hits[k] * targets[k]
        IntVar total = new IntVar(store, "total", 0, totalMax);
        sumVars[n] = total;
        sumWeights[n] = -1;
        store.impose(new LinearInt(sumVars, sumWeights, "==", 0));

        // diff = total - target (signed), dev = |diff| is the deviation to minimise
        IntVar diff = new IntVar(store, "diff", -target, totalMax - target);
        store.impose(new LinearInt(new IntVar[]{total, diff},
                new int[]{1, -1}, "==", target));
        IntVar dev = new IntVar(store, "deviation", 0, Math.max(target, totalMax - target));
        store.impose(new AbsXeqY(diff, dev));

        return new Model().put("hits", hits).minimize(dev);
    }
}
