// Jobs puzzle: four people (0-3) each hold exactly two of eight jobs. Find which person holds each job.
// Each job variable gives the person holding it. Each job is held by one person, and each person holds two jobs.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.Reified;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XneqC;
import org.jacop.constraints.XneqY;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {

    static final int PEOPLE = 4;
    static final int JOBS = 8;

    public static Model build(JSONObject instance, Store store) {
        // Job indices: 0 chef, 1 guard, 2 nurse, 3 clerk, 4 police officer, 5 teacher, 6 actor, 7 boxer.
        IntVar[] job = new IntVar[JOBS];
        for (int j = 0; j < JOBS; j++) {
            job[j] = new IntVar(store, "job" + j, 0, PEOPLE - 1);
        }
        final int CHEF = 0, NURSE = 2, CLERK = 3, POLICE = 4, TEACHER = 5, BOXER = 7;

        // Each person holds exactly two jobs.
        // holds[j][k] = 1 when job j is held by person k.
        BooleanVar[][] holds = new BooleanVar[JOBS][PEOPLE];
        for (int j = 0; j < JOBS; j++) {
            for (int k = 0; k < PEOPLE; k++) {
                holds[j][k] = new BooleanVar(store, "holds" + j + "_" + k);
                store.impose(new Reified(new XeqC(job[j], k), holds[j][k]));
            }
        }
        for (int k = 0; k < PEOPLE; k++) {
            IntVar[] column = new IntVar[JOBS];
            int[] ones = new int[JOBS];
            for (int j = 0; j < JOBS; j++) {
                column[j] = holds[j][k];
                ones[j] = 1;
            }
            store.impose(new LinearInt(column, ones, "==", 2));
        }

        // 1. The nurse is not a teacher, police officer, or clerk.
        store.impose(new XneqY(job[NURSE], job[TEACHER]));
        store.impose(new XneqY(job[NURSE], job[POLICE]));
        store.impose(new XneqY(job[NURSE], job[CLERK]));
        // 2. The clerk is not the chef.
        store.impose(new XneqY(job[CLERK], job[CHEF]));
        // 3. Person 0 is not the boxer.
        store.impose(new XneqC(job[BOXER], 0));
        // 4. Person 3 is not the teacher, police officer, or nurse.
        store.impose(new XneqC(job[TEACHER], 3));
        store.impose(new XneqC(job[POLICE], 3));
        store.impose(new XneqC(job[NURSE], 3));
        // 5. Person 0, the chef, and the police officer went golfing together: three different people,
        //    so the chef and the police officer are neither person 0 nor each other.
        store.impose(new XneqC(job[CHEF], 0));
        store.impose(new XneqC(job[POLICE], 0));
        store.impose(new XneqY(job[CHEF], job[POLICE]));

        return new Model().put("chef", job[0]).put("guard", job[1]).put("nurse", job[2])
            .put("clerk", job[3]).put("police_officer", job[4]).put("teacher", job[5])
            .put("actor", job[6]).put("boxer", job[7])
            .search(job, null, null);
    }
}
