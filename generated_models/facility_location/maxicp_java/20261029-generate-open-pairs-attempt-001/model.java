import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.maxicp.cp.engine.constraints.CostCardinalityMaxDC;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Facility location: choose which of the four warehouses (New York, Los Angeles, Chicago,
// Atlanta) to open and how many units each ships to each region, so that every region's demand is
// met, a warehouse ships at most max_shipping units in total and only when open, the opening rules
// hold, and the fixed costs plus the shipping costs are as small as possible.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    String[] names = inst.getStringArray("warehouse_s");
    int[] fixedCost = inst.getIntArray("fixed_costs");
    int capacity = inst.getInt("max_shipping");
    int[] demand = inst.getIntArray("demands");
    int[][] unitCost = inst.getIntMatrix("shipping_costs");
    int nW = names.length, nR = demand.length;
    CPSolver cp = m.cp();
    List<String> city = Arrays.asList(names);
    int newYork = city.indexOf("New York"), losAngeles = city.indexOf("Los Angeles"), atlanta = city.indexOf("Atlanta");

    // open[w]: whether warehouse w is opened (registered first, so the search decides them first)
    CPBoolVar[] open = m.boolVarArray(nW);

    // 1. if the New York warehouse is opened, the Los Angeles one is opened too
    cp.post(implies(open[newYork], open[losAngeles]));
    // 2. no more than three warehouses are operational
    cp.post(le(sum(open), 3));
    // 3. the Atlanta or the Los Angeles warehouse is opened
    cp.post(or(open[atlanta], open[losAngeles]));

    // Every unit of demand is shipped from one warehouse: unit u of region j picks its warehouse.
    // The units of one region are interchangeable, so each region's units are listed in order of
    // the warehouse they use; the shipments (the counts) are what the problem asks for, and every
    // shipment plan has exactly one such listing. rank[u] is the position of the warehouse in the
    // region's list of warehouses by increasing shipping cost, so the search tries cheap routes first.
    List<CPIntVar> from = new ArrayList<>();
    List<int[]> costOf = new ArrayList<>();
    List<Integer> regionOf = new ArrayList<>();
    for (int j = 0; j < nR; j++) {
      final int region = j;
      Integer[] byCost = new Integer[nW];
      for (int w = 0; w < nW; w++) byCost[w] = w;
      Arrays.sort(byCost, (a, b) -> unitCost[a][region] != unitCost[b][region]
          ? Integer.compare(unitCost[a][region], unitCost[b][region]) : Integer.compare(a, b));
      int[] warehouseAt = new int[nW];
      for (int k = 0; k < nW; k++) warehouseAt[k] = byCost[k];
      CPIntVar previous = null;
      for (int u = 0; u < demand[j]; u++) {
        CPIntVar rank = m.intVar(0, nW - 1);
        if (previous != null) cp.post(le(previous, rank));
        previous = rank;
        from.add(element(warehouseAt, rank));
        int[] c = new int[nW];
        for (int w = 0; w < nW; w++) c[w] = unitCost[w][j];
        costOf.add(c);
        regionOf.add(j);
      }
    }
    CPIntVar[] unitFrom = from.toArray(new CPIntVar[0]);
    int[][] unitCosts = costOf.toArray(new int[0][]);

    // ships[w][j]: the units region j receives from warehouse w; every region's demand is met
    // because each of its units comes from exactly one warehouse
    CPIntVar[][] ships = new CPIntVar[nW][nR];
    for (int w = 0; w < nW; w++) {
      List<List<CPBoolVar>> perRegion = new ArrayList<>();
      for (int j = 0; j < nR; j++) perRegion.add(new ArrayList<>());
      for (int u = 0; u < unitFrom.length; u++) perRegion.get(regionOf.get(u)).add(isEq(unitFrom[u], w));
      CPIntVar[] shipped = new CPIntVar[nR];
      for (int j = 0; j < nR; j++) shipped[j] = ships[w][j] = sum(perRegion.get(j).toArray(new CPBoolVar[0]));
      // a warehouse ships at most max_shipping units in total, and nothing when it is closed
      cp.post(le(sum(shipped), mul(open[w], capacity)));
    }

    // the shipping cost; the cost-cardinality constraint bounds it below by the cheapest
    // transportation plan the remaining choices allow (a min-cost flow with the capacities)
    int maxShipping = 0;
    for (int[] c : unitCosts) maxShipping += Arrays.stream(c).max().getAsInt();
    CPIntVar shipping = makeIntVar(cp, 0, maxShipping);
    int[] cardinality = new int[nW];
    Arrays.fill(cardinality, capacity);
    cp.post(new CostCardinalityMaxDC(unitFrom, cardinality, unitCosts, shipping));
    CPIntVar[] terms = new CPIntVar[nW + 1];
    for (int w = 0; w < nW; w++) terms[w] = mul(open[w], fixedCost[w]);
    terms[nW] = shipping;
    // total cost: the fixed costs of the open warehouses plus the shipping costs, to minimise
    CPIntVar totalCost = sum(terms);
    m.minimize(totalCost);

    out.put("total_cost", totalCost);
    out.put("open_warehouse", open);
    out.put("ships", ships);
  }
}
