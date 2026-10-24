// Template design (CSPLib 002): print a set of mother sheets for a family of design variations.
// Each template is an aluminium plate with n_slots slots; each slot carries one variation,
// and a template may leave slots empty. Template t is printed production[t] times. The
// layout[t][v] is the number of slots on template t that carry variation v. Every variation
// v must be printed at least demand[v] times in total. Minimise the total number of sheets printed.
import org.jacop.constraints.LinearInt;
import org.jacop.constraints.XmulYeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int slots = inst.getInt("n_slots");
        int templates = inst.getInt("n_templates");
        int variations = inst.getInt("n_var");
        JSONArray demandJson = inst.getJSONArray("demand");

        int[] demand = new int[variations];
        int totalDemand = 0;
        for (int v = 0; v < variations; v++) {
            demand[v] = demandJson.getInt(v);
            totalDemand += demand[v];
        }

        // layout[t][v]: number of slots on template t that carry variation v
        IntVar[][] layout = new IntVar[templates][variations];
        for (int t = 0; t < templates; t++) {
            for (int v = 0; v < variations; v++) {
                layout[t][v] = new IntVar(store, "layout_" + t + "_" + v, 0, slots);
            }
        }

        // production[t]: number of sheets printed from template t. If a template with
        // layout[t][v] >= 1 prints more than the largest demand, printing fewer sheets still covers
        // every variation it carries, so no count above the largest demand is needed.
        int maxDemand = 0;
        for (int v = 0; v < variations; v++) {
            maxDemand = Math.max(maxDemand, demand[v]);
        }
        IntVar[] production = new IntVar[templates];
        for (int t = 0; t < templates; t++) {
            production[t] = new IntVar(store, "production_" + t, 0, maxDemand);
        }

        // a template has at most n_slots slots, so the layout counts add up to at most n_slots
        for (int t = 0; t < templates; t++) {
            store.impose(new LinearInt(layout[t], unitWeights(variations), "<=", slots));
        }

        // copies of variation v printed from template t: layout[t][v] * production[t]
        IntVar[][] copies = new IntVar[templates][variations];
        for (int t = 0; t < templates; t++) {
            for (int v = 0; v < variations; v++) {
                copies[t][v] = new IntVar(store, "copies_" + t + "_" + v, 0, slots * totalDemand);
                store.impose(new XmulYeqZ(layout[t][v], production[t], copies[t][v]));
            }
        }

        // a sheet from template t carries at most n_slots copies: the copies of template t
        // are at most n_slots times its production (redundant with the layout bound)
        for (int t = 0; t < templates; t++) {
            IntVar[] perSheet = new IntVar[variations + 1];
            int[] perSheetWeights = new int[variations + 1];
            for (int v = 0; v < variations; v++) {
                perSheet[v] = copies[t][v];
                perSheetWeights[v] = 1;
            }
            perSheet[variations] = production[t];
            perSheetWeights[variations] = -slots;
            store.impose(new LinearInt(perSheet, perSheetWeights, "<=", 0));
        }

        // the copies of each variation, summed over all templates, meet its demand
        for (int v = 0; v < variations; v++) {
            IntVar[] column = new IntVar[templates];
            for (int t = 0; t < templates; t++) {
                column[t] = copies[t][v];
            }
            store.impose(new LinearInt(column, unitWeights(templates), ">=", demand[v]));
        }

        // objective: the total number of sheets printed over all templates
        IntVar total = new IntVar(store, "total_sheets", 0, templates * maxDemand);
        // the total is the sum of the production counts
        IntVar[] sheets = new IntVar[templates + 1];
        int[] sheetWeights = new int[templates + 1];
        for (int t = 0; t < templates; t++) {
            sheets[t] = production[t];
            sheetWeights[t] = 1;
        }
        sheets[templates] = total;
        sheetWeights[templates] = -1;
        store.impose(new LinearInt(sheets, sheetWeights, "==", 0));
        // every sheet carries at most n_slots copies, so the copies of all variations
        // sum to at most n_slots times the total number of sheets; the copies must
        // cover the total demand. Together they bound the number of sheets from below.
        {
            IntVar[] all = new IntVar[templates * variations + 1];
            int[] allWeights = new int[templates * variations + 1];
            for (int t = 0; t < templates; t++) {
                for (int v = 0; v < variations; v++) {
                    all[t * variations + v] = copies[t][v];
                    allWeights[t * variations + v] = 1;
                }
            }
            all[templates * variations] = total;
            allWeights[templates * variations] = -slots;
            store.impose(new LinearInt(all, allWeights, "<=", 0));
            store.impose(new LinearInt(java.util.Arrays.copyOf(all, templates * variations),
                unitWeights(templates * variations), ">=", totalDemand));
        }

        // label the layouts first (small domains), then the production counts; the copies follow
        IntVar[] decisions = new IntVar[templates * variations + templates];
        for (int t = 0; t < templates; t++) {
            for (int v = 0; v < variations; v++) {
                decisions[t * variations + v] = layout[t][v];
            }
        }
        for (int t = 0; t < templates; t++) {
            decisions[templates * variations + t] = production[t];
        }

        Model model = new Model().put("layout", layout).put("production", production);
        return model.search(decisions, null, null).minimize(total);
    }

    private static int[] unitWeights(int n) {
        int[] w = new int[n];
        for (int i = 0; i < n; i++) {
            w[i] = 1;
        }
        return w;
    }
}
