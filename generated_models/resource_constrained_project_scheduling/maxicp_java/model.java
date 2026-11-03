import org.maxicp.Constants;
import org.maxicp.cp.engine.constraints.scheduling.CPCumulFunction;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPIntervalVar;
import org.maxicp.cp.engine.core.CPSolver;
import java.util.ArrayList;
import java.util.List;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Resource-constrained project scheduling: give every job a start time so that each job starts
// after all its predecessors have finished, the jobs running at any time never need more of a
// resource than its capacity, and the makespan (the time the last job ends) is as small as possible.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] duration = inst.getIntArray("durations_data");
    int[][] need = inst.getIntMatrix("resource_needs_data");
    int[] capacity = inst.getIntArray("resource_capacities_data");
    int[][] links = inst.getIntMatrix("successors_link_data");
    int n = duration.length, nRes = capacity.length;
    CPSolver cp = m.cp();

    // the horizon: running the jobs one after the other always works, so no optimal schedule ends later
    int horizon = 0;
    for (int d : duration) horizon += d;

    // job[i]: an interval of length duration[i] that must be scheduled, starting from time 0
    CPIntervalVar[] job = new CPIntervalVar[n];
    CPIntVar[] start = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      job[i] = makeIntervalVar(cp, false, duration[i]);
      cp.post(startAfter(job[i], 0));
      cp.post(le(end(job[i]), horizon));
      start[i] = start(job[i]);
    }

    // a job starts only after each of its predecessors has finished
    for (int[] link : links) cp.post(endBeforeStart(job[link[0]], job[link[1]]));

    // at every time the running jobs need at most the capacity of each resource
    for (int r = 0; r < nRes; r++) {
      CPCumulFunction usage = flat();
      for (int i = 0; i < n; i++) if (need[i][r] > 0 && duration[i] > 0) usage = plus(usage, pulse(job[i], need[i][r]));
      cp.post(le(usage, capacity[r], Constants.CumulativeAlgo.BELDICEANU_CARLSSON));
    }

    // Implied by the capacities: two jobs whose needs of some resource add up to more than its
    // capacity can never run at the same time. Groups of jobs that are pairwise in this situation
    // run one at a time, so each group is posted as a no-overlap (a unary resource), whose
    // propagation is much stronger than the cumulative's on those jobs. The groups are built
    // greedily: start from each conflicting pair not yet covered and add every job that conflicts
    // with all members.
    boolean[][] clash = new boolean[n][n];
    for (int i = 0; i < n; i++)
      for (int j = 0; j < n; j++)
        if (i != j && duration[i] > 0 && duration[j] > 0)
          for (int r = 0; r < nRes; r++) if (need[i][r] + need[j][r] > capacity[r]) clash[i][j] = true;
    boolean[][] covered = new boolean[n][n];
    for (int i = 0; i < n; i++)
      for (int j = i + 1; j < n; j++) {
        if (!clash[i][j] || covered[i][j]) continue;
        List<Integer> group = new ArrayList<>(List.of(i, j));
        for (int k = 0; k < n; k++) {
          if (group.contains(k)) continue;
          boolean all = true;
          for (int g : group) all &= clash[k][g];
          if (all) group.add(k);
        }
        for (int a : group) for (int b : group) covered[a][b] = true;
        CPIntervalVar[] members = new CPIntervalVar[group.size()];
        for (int k = 0; k < members.length; k++) members[k] = job[group.get(k)];
        cp.post(noOverlap(members));
      }

    // Order decisions: for every pair of jobs that can never overlap, whether the first runs
    // before the second. They are registered, so the search orders those pairs before it sets
    // start times (precedence posting), which prunes better than branching on times alone.
    for (int i = 0; i < n; i++)
      for (int j = i + 1; j < n; j++)
        if (clash[i][j]) {
          CPBoolVar first = m.boolVar();
          cp.post(eq(first, isLe(end(job[i]), start(job[j]))));
          cp.post(eq(not(first), isLe(end(job[j]), start(job[i]))));
        }

    // the makespan, to be minimised
    CPIntVar makespan = makespan(job);
    m.minimize(makespan);

    out.put("start_time", start);
  }
}
