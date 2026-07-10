// Study-5 Family-XL adapter shim (pair: descstats.java, Amendment A3).
// Adapter/oracle layer only: calls the unmodified external entry points
// (Commons Math stat.descriptive pipeline); frozen aux documented in
// docs/prereg_v2/STUDY5_XL_ROSTER.md §A3.
import java.io.BufferedReader;
import java.io.InputStreamReader;


public class Main {
    static final double PHI = 1.6180339887498949;

    static double program(double x) {
        double w = 0.4 * Math.pow(2.0, 2.0 * x - 1.0);
        org.apache.commons.math3.stat.descriptive.DescriptiveStatistics ds =
            new org.apache.commons.math3.stat.descriptive.DescriptiveStatistics();
        for (int i = 1; i <= 256; i++) {
            double ui = i * PHI;
            ui -= Math.floor(ui);
            ds.addValue(0.5 + (ui - 0.5) * w);
        }
        return ds.getStandardDeviation();
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line;
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (line.isEmpty()) continue;
            double x = Double.parseDouble(line);
            double y;
            try { y = program(x); } catch (Exception e) { y = Double.NaN; }
            System.out.printf(java.util.Locale.ROOT, "%.17g%n", y);
            System.out.flush();
        }
    }
}
