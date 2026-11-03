// Contracting costs: a contractor pays six tradesmen (paper hanger, painter, plumber,
// electrician, carpenter, mason). Each stated payment is the sum of the two named
// men's charges. Find what each man charges, in dollars.
import org.jacop.constraints.*;
import org.jacop.core.*;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        // a charge is a whole number of dollars; the largest payment in the statement is 5300
        final int maxCharge = 5300;

        IntVar paperHanger = new IntVar(store, "paper_hanger", 0, maxCharge);
        IntVar painter = new IntVar(store, "painter", 0, maxCharge);
        IntVar plumber = new IntVar(store, "plumber", 0, maxCharge);
        IntVar electrician = new IntVar(store, "electrician", 0, maxCharge);
        IntVar carpenter = new IntVar(store, "carpenter", 0, maxCharge);
        IntVar mason = new IntVar(store, "mason", 0, maxCharge);

        // $1,100 to the paper hanger and the painter
        store.impose(new XplusYeqC(paperHanger, painter, 1100));
        // $1,700 to the painter and plumber
        store.impose(new XplusYeqC(painter, plumber, 1700));
        // $1,100 to the plumber and electrician
        store.impose(new XplusYeqC(plumber, electrician, 1100));
        // $3,300 to the electrician and carpenter
        store.impose(new XplusYeqC(electrician, carpenter, 3300));
        // $5,300 to the carpenter and mason
        store.impose(new XplusYeqC(carpenter, mason, 5300));
        // $3,200 to the mason and painter
        store.impose(new XplusYeqC(mason, painter, 3200));

        return new Model().put("paper_hanger", paperHanger).put("painter", painter)
                .put("plumber", plumber).put("electrician", electrician)
                .put("carpenter", carpenter).put("mason", mason);
    }
}
