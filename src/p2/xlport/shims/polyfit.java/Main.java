// Study-5 Family-XL adapter shim (pair: polyfit.java, Amendment A3).
// Adapter/oracle layer only: calls the unmodified external entry points
// (Commons Math fitting module: PolynomialCurveFitter over the
// Levenberg-Marquardt optimizer chain); frozen aux documented in
// docs/prereg_v2/STUDY5_XL_ROSTER.md §A3.
import java.io.BufferedReader;
import java.io.InputStreamReader;


public class Main {
    static double program(double x) {
        double a = 0.5 + x;
        org.apache.commons.math3.fitting.WeightedObservedPoints obs =
            new org.apache.commons.math3.fitting.WeightedObservedPoints();
        for (int j = 0; j <= 32; j++) {
            double t = j / 32.0;
            obs.add(t, Math.exp(a * t));
        }
        org.apache.commons.math3.fitting.PolynomialCurveFitter fitter =
            org.apache.commons.math3.fitting.PolynomialCurveFitter.create(3);
        double[] coef = fitter.fit(obs.toList());   // increasing degree order
        org.apache.commons.math3.analysis.polynomials.PolynomialFunction p =
            new org.apache.commons.math3.analysis.polynomials.PolynomialFunction(coef);
        return p.value(0.6);
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
