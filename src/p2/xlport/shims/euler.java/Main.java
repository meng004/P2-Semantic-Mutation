// Study-5 Family-XL adapter shim (pair: euler.java). Adapter/oracle layer only:
// calls the unmodified external entry point(s); frozen aux documented in
// docs/prereg_v2/STUDY5_XL_ROSTER.md.
import java.io.BufferedReader;
import java.io.InputStreamReader;
import com.thealgorithms.maths.EulerMethod;
import java.util.ArrayList;

public class Main {
    static double program(double x) {
        double y0 = 0.05 + 0.9 * x;
        ArrayList<double[]> tr = EulerMethod.eulerFull(
            0.0, 2.0, 0.0078125, y0, (a, b) -> b * (1.0 - b));
        return tr.get(tr.size() - 1)[1];
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
