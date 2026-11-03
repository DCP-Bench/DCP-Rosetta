// Warehouse location (CSPLib 034): choose which warehouses to open and which open warehouse
// supplies each store. Every store is supplied by exactly one open warehouse, and no warehouse
// supplies more stores than its capacity. Minimise the total cost: the fixed maintenance cost
// of every open warehouse plus the supply cost of every store from its warehouse.
// Indices are 0-based, as in the instance: warehouse w in 0..n_suppliers-1, store s in 0..n_stores-1.
// Search: the supplier assignment is labelled first. Once every store is assigned, the open
// warehouses and the costs are fixed by propagation, so the search does not branch on them.

import org.jacop.constraints.Count;
import org.jacop.constraints.Element;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XlteqC;
import org.jacop.constraints.XmulCeqZ;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONArray;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int buildingCost = inst.getInt("building_cost");  // maintenance cost of one open warehouse
        JSONArray capacityJson = inst.getJSONArray("capacity");
        JSONArray costJson = inst.getJSONArray("cost_matrix");  // costJson[s][w]: supply cost of store s from warehouse w
        int nStores = inst.getInt("n_stores");
        int nWarehouses = capacityJson.length();                 // n_suppliers in the description

        // open_warehouses[w] = 1 if warehouse w is open
        BooleanVar[] open = new BooleanVar[nWarehouses];
        for (int w = 0; w < nWarehouses; w++) {
            open[w] = new BooleanVar(store, "open" + w);
        }

        // supplier_assignment[s] = the warehouse that supplies store s
        IntVar[] assign = new IntVar[nStores];
        for (int s = 0; s < nStores; s++) {
            assign[s] = new IntVar(store, 0, nWarehouses - 1);
        }

        // a store can only be supplied by an open warehouse: open[assign[s]] = 1.
        // Element.choose returns a constraint, which must be imposed on the store.
        for (int s = 0; s < nStores; s++) {
            IntVar isOpen = new IntVar(store, 0, 1);
            store.impose(Element.choose(assign[s], open, isOpen, -1));  // -1: 0-based index
            store.impose(new XeqC(isOpen, 1));
        }

        // capacity: the number of stores assigned to warehouse w is at most capacity[w]
        for (int w = 0; w < nWarehouses; w++) {
            int cap = capacityJson.getInt(w);
            IntVar load = new IntVar(store, 0, Math.min(cap, nStores));
            store.impose(new Count(assign, load, w));
            store.impose(new XlteqC(load, cap));
        }

        // cost of each store: supply cost from the warehouse that serves it
        IntVar[] costs = new IntVar[nStores];
        int maxCost = 0;
        for (int s = 0; s < nStores; s++) {
            JSONArray row = costJson.getJSONArray(s);
            int[] rowCosts = new int[nWarehouses];
            int rowMin = Integer.MAX_VALUE;
            int rowMax = 0;
            for (int w = 0; w < nWarehouses; w++) {
                rowCosts[w] = row.getInt(w);
                rowMin = Math.min(rowMin, rowCosts[w]);
                rowMax = Math.max(rowMax, rowCosts[w]);
            }
            maxCost += rowMax;
            costs[s] = new IntVar(store, rowMin, rowMax);
            store.impose(Element.choose(assign[s], rowCosts, costs[s], -1));
        }

        // maintenance cost of each warehouse: buildingCost if open, else 0
        IntVar[] terms = new IntVar[nWarehouses + nStores];
        for (int w = 0; w < nWarehouses; w++) {
            IntVar maint = new IntVar(store, 0, buildingCost);
            store.impose(new XmulCeqZ(open[w], buildingCost, maint));
            terms[w] = maint;
        }
        for (int s = 0; s < nStores; s++) {
            terms[nWarehouses + s] = costs[s];
        }

        // objective: total cost = maintenance of the open warehouses + supply costs
        int upper = buildingCost * nWarehouses + maxCost;
        IntVar total = new IntVar(store, 0, upper);
        store.impose(new SumInt(terms, "==", total));

        return new Model()
                .put("open_warehouses", open)
                .put("supplier_assignment", assign)
                .put("total_cost", total)
                .search(assign, null, null)
                .minimize(total);
    }
}
