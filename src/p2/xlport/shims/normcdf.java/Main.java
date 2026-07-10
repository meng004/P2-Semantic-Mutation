// Study-5 Family-XL adapter shim (pair: normcdf.java). Adapter/oracle layer only:
// calls the unmodified external entry point(s); frozen aux documented in
// docs/prereg_v2/STUDY5_XL_ROSTER.md.
import java.io.BufferedReader;
import java.io.InputStreamReader;


public class Main {
    static final org.apache.commons.math3.distribution.NormalDistribution ND =
        new org.apache.commons.math3.distribution.NormalDistribution();

    static double program(double x) {
        return ND.cumulativeProbability(6.0 * x - 3.0);
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
