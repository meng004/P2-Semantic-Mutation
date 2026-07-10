# Study-5 Family-XL adapter shim (pair: sinc.jl). Adapter/oracle layer only:
# calls the unmodified Julia stdlib entry point; frozen aux documented in
# docs/prereg_v2/STUDY5_XL_ROSTER.md.

using Printf

program(x) = sinc(4.0 * x - 2.0)

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
