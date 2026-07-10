// Study-5 Family-XL adapter shim (pair: rungekutta.java, Amendment A3).
// Adapter/oracle layer only: calls the unmodified external entry points
// (Commons Math ode.nonstiff module: ClassicalRungeKuttaIntegrator fixed
// step); frozen aux (A1 program 'rungekutta', verbatim) documented in
// docs/prereg_v2/STUDY5_XL_ROSTER.md §A3.
import java.io.BufferedReader;
import java.io.InputStreamReader;


public class Main {
    static double program(double x) {
        org.apache.commons.math3.ode.FirstOrderDifferentialEquations ode =
            new org.apache.commons.math3.ode.FirstOrderDifferentialEquations() {
                public int getDimension() { return 1; }
                public void computeDerivatives(double t, double[] y,
                                               double[] yDot) {
                    yDot[0] = (t - y[0]) / 2.0;
                }
            };
        org.apache.commons.math3.ode.nonstiff.ClassicalRungeKuttaIntegrator integ =
            new org.apache.commons.math3.ode.nonstiff.ClassicalRungeKuttaIntegrator(
                0.015625);   // h = 1/64 dyadic (A1 aux)
        double[] y = new double[] {x};
        integ.integrate(ode, 0.0, y, 2.0, y);
        return y[0];
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
