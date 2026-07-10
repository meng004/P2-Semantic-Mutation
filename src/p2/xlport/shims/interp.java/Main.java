// Study-5 Family-XL adapter shim (pair: interp.java, Amendment A3).
// Adapter/oracle layer only: calls the unmodified external entry points
// (Commons Math analysis.interpolation module); frozen aux documented in
// docs/prereg_v2/STUDY5_XL_ROSTER.md §A3.
import java.io.BufferedReader;
import java.io.InputStreamReader;


public class Main {
    static double program(double x) {
        final int n = 17;
        double[] t = new double[n];
        double[] v = new double[n];
        for (int j = 0; j < n; j++) {
            t[j] = j / 16.0;
            v[j] = Math.exp(t[j]);
        }
        org.apache.commons.math3.analysis.interpolation.LinearInterpolator li =
            new org.apache.commons.math3.analysis.interpolation.LinearInterpolator();
        org.apache.commons.math3.analysis.polynomials.PolynomialSplineFunction f =
            li.interpolate(t, v);
        return f.value(x);
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
