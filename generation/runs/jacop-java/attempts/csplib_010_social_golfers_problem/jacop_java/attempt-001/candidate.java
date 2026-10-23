// Social golfers problem: schedule n_groups * group_size golfers into n_groups groups of
// group_size golfers each, for n_weeks weeks, so that no two golfers share a group more
// than once. assign[i][w] is the group (0-based) of golfer i in week w.
// Sizes come from the instance fields n_groups, group_size and n_weeks.
import org.jacop.constraints.Count;
import org.jacop.constraints.Reified;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XeqY;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {

    public static Model build(JSONObject inst, Store store) {
        int nGroups = inst.getInt("n_groups");
        int groupSize = inst.getInt("group_size");
        int nWeeks = inst.getInt("n_weeks");
        int nGolfers = nGroups * groupSize;

        // assign[i][w]: the group of golfer i in week w, one of 0..nGroups-1.
        IntVar[][] assign = new IntVar[nGolfers][nWeeks];
        for (int i = 0; i < nGolfers; i++)
            for (int w = 0; w < nWeeks; w++)
                assign[i][w] = new IntVar(store, "assign_" + i + "_" + w, 0, nGroups - 1);

        // Each week, every group has exactly group_size golfers.
        for (int w = 0; w < nWeeks; w++) {
            IntVar[] week = new IntVar[nGolfers];
            for (int i = 0; i < nGolfers; i++) week[i] = assign[i][w];
            for (int g = 0; g < nGroups; g++) {
                IntVar size = new IntVar(store, groupSize, groupSize);
                store.impose(new Count(week, size, g));
            }
        }

        // No two golfers play together more than once: for each pair, the number of weeks in
        // which they are in the same group is at most 1. same[p][w] is 1 when the pair p is
        // in the same group in week w.
        for (int i = 0; i < nGolfers; i++) {
            for (int j = i + 1; j < nGolfers; j++) {
                IntVar[] same = new IntVar[nWeeks];
                for (int w = 0; w < nWeeks; w++) {
                    same[w] = new IntVar(store, "same_" + i + "_" + j + "_" + w, 0, 1);
                    store.impose(new Reified(new XeqY(assign[i][w], assign[j][w]), same[w]));
                }
                store.impose(new SumInt(same, "<=", new IntVar(store, 1, 1)));
            }
        }

        // Label the assignment variables first, week by week. The pair variables are then fixed
        // by propagation, so the search does not branch on them.
        IntVar[] order = new IntVar[nGolfers * nWeeks];
        for (int w = 0; w < nWeeks; w++)
            for (int i = 0; i < nGolfers; i++)
                order[w * nGolfers + i] = assign[i][w];

        return new Model().put("assign", assign).search(order, null, null);
    }
}
