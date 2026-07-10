// Study-5 Family-XL adapter shim (pair: invsqrt.go). Adapter/oracle layer
// only: calls the unmodified external entry point; frozen aux documented in
// docs/prereg_v2/STUDY5_XL_ROSTER.md.
package main

import (
	"bufio"
	"fmt"
	"math"
	"os"
	"strconv"
	"strings"

	"xlpair/binary"
)

func main() {
	sc := bufio.NewScanner(os.Stdin)
	out := bufio.NewWriter(os.Stdout)
	for sc.Scan() {
		s := strings.TrimSpace(sc.Text())
		if s == "" {
			continue
		}
		x, err := strconv.ParseFloat(s, 64)
		if err != nil {
			continue
		}
		u := math.Pow(4.0, 2.0*x-1.0)
		y := float64(binary.FastInverseSqrt(float32(u)))
		fmt.Fprintf(out, "%.17g\n", y)
		out.Flush()
	}
}
