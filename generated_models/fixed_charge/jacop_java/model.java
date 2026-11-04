// Fixed charge problem: a company makes products and each product needs one rented machine.
// Choose how many units of each product to make, and which machines to rent, to maximise profit.
// Profit: the unit profit of each product, times the units made, minus the rent of each machine
// that is rented. A product can only be made when its machine is rented.
// Resource limits: the labour and cloth used by all products stay within the capacities.
//
// Data layout in the instance (0-based indices):
//   product[p][0] = profit per unit of product p, product[p][1] = the machine product p needs
//   use[p][r]     = amount of resource r used per unit of product p
//   resources     = resource ids, in the order of capacity[]
//   renting_cost[m] = rent of machine m, machines = machine ids
//   max_production  = upper bound on units made of any product
//
// Variables: made[p] = units of product p; rented[m] = 1 if machine m is rented.
// The objective variable z is tied to the profit by one linear equation.

import org.jacop.constraints.LinearInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int numProducts = inst.getInt("num_products");
        int numMachines = inst.getInt("num_machines");
        int numResources = inst.getJSONArray("capacity").length();
        int maxProduction = inst.getInt("max_production");
        JSONArray productJson = inst.getJSONArray("product");
        JSONArray useJson = inst.getJSONArray("use");
        JSONArray capacityJson = inst.getJSONArray("capacity");
        JSONArray rentJson = inst.getJSONArray("renting_cost");

        // made[p] = units of product p to make
        IntVar[] made = new IntVar[numProducts];
        for (int p = 0; p < numProducts; p++) {
            made[p] = new IntVar(store, 0, maxProduction);
        }

        // rented[m] = 1 if machine m is rented
        BooleanVar[] rented = new BooleanVar[numMachines];
        for (int m = 0; m < numMachines; m++) {
            rented[m] = new BooleanVar(store, "rent" + m);
        }

        // a product can only be made on a rented machine: made[p] <= maxProduction * rented[machine(p)]
        for (int p = 0; p < numProducts; p++) {
            int machine = productJson.getJSONArray(p).getInt(1);
            store.impose(new LinearInt(
                    new IntVar[]{made[p], rented[machine]},
                    new int[]{1, -maxProduction},
                    "<=", 0));
        }

        // resource capacities: the total use of each resource stays within its capacity
        for (int r = 0; r < numResources; r++) {
            int[] weights = new int[numProducts];
            for (int p = 0; p < numProducts; p++) {
                weights[p] = useJson.getJSONArray(p).getInt(r);
            }
            store.impose(new LinearInt(made, weights, "<=", capacityJson.getInt(r)));
        }

        // profit = sum of unit profit * units made - sum of rent of rented machines.
        // Written as one equation with the objective variable z:
        //   sum profit[p] * made[p] - sum rent[m] * rented[m] - z = 0
        int rentTotal = 0;
        int profitTotal = 0;
        int numTerms = numProducts + numMachines + 1;
        IntVar[] terms = new IntVar[numTerms];
        int[] weights = new int[numTerms];
        for (int p = 0; p < numProducts; p++) {
            int profit = productJson.getJSONArray(p).getInt(0);
            terms[p] = made[p];
            weights[p] = profit;
            profitTotal += profit * maxProduction;
        }
        for (int m = 0; m < numMachines; m++) {
            int rent = rentJson.getInt(m);
            terms[numProducts + m] = rented[m];
            weights[numProducts + m] = -rent;
            rentTotal += rent;
        }
        IntVar z = new IntVar(store, -rentTotal, profitTotal);
        terms[numTerms - 1] = z;
        weights[numTerms - 1] = -1;
        store.impose(new LinearInt(terms, weights, "==", 0));

        return new Model().put("z", z).maximize(z);
    }
}
