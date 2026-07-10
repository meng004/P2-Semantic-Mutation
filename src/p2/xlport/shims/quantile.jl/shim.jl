# Study-5 Family-XL adapter shim (pair: quantile.jl). Adapter/oracle layer only:
# calls the unmodified Julia stdlib entry point; frozen aux documented in
# docs/prereg_v2/STUDY5_XL_ROSTER.md.
using Statistics
using Printf

const V = [-3.7, -2.9, -2.3, -1.7, -1.3, -0.9, -0.6, -0.35, -0.2, -0.08, 0.0, 0.08, 0.2, 0.35, 0.6, 0.9, 1.3, 1.7, 2.3, 2.9, 3.7]

program(x) = quantile(V, x)

while !eof(stdin)
    line = readline(stdin)
    s = strip(line)
    isempty(s) && continue
    x = try
        parse(Float64, s)
    catch
        continue
    end
    y = program(x)
    @printf("%.17g\n", y)
    flush(stdout)
end
