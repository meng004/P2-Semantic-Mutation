#!/usr/bin/env python3
"""C-LAMMPS-001: quantify logo reassembly between start.dump and end.dump.

Positions are compared per atom id with minimum-image wrapping in the final
(orthogonal-again) periodic box; velocities are compared against the negated
initial velocities (a perfect reversal ends with v_end = -v_start since the
final no-integrator segments do not move atoms).
"""
import math
import statistics
import sys

def read_dump(path):
    with open(path) as f:
        lines = f.readlines()
    n = int(lines[3])
    box = []
    for i in (5, 6, 7):
        box.append([float(v) for v in lines[i].split()])
    cols = lines[8].split()[2:]
    data = {}
    for ln in lines[9:9 + n]:
        v = ln.split()
        rec = dict(zip(cols, v))
        data[int(rec["id"])] = [float(rec[c]) for c in ("x", "y", "vx", "vy")]
    return data, box

start, box0 = read_dump(sys.argv[1])
end, box1 = read_dump(sys.argv[2])
lx = box1[0][1] - box1[0][0] - (box1[0][2] if len(box1[0]) > 2 else 0) * 0  # plain bounds
# for triclinic dumps LAMMPS writes xlo_bound xhi_bound xy; handle both
xy = box1[0][2] if len(box1[0]) > 2 else 0.0
ly = box1[1][1] - box1[1][0]
lx = (box1[0][1] - box1[0][0]) - abs(xy)

ids = sorted(start)
dpos = []
dvel = []
for i in ids:
    x0, y0, vx0, vy0 = start[i]
    x1, y1, vx1, vy1 = end[i]
    dx, dy = x1 - x0, y1 - y0
    # minimum image (small residual tilt folded into x via xy*round(dy/ly))
    dy -= ly * round(dy / ly)
    dx -= xy * round((y1 - y0) / ly)
    dx -= lx * round(dx / lx)
    dpos.append(math.hypot(dx, dy))
    dvel.append(math.hypot(vx1 + vx0, vy1 + vy0))

rms = lambda a: math.sqrt(sum(v * v for v in a) / len(a))
print(f"atoms={len(ids)} box tilt xy(end)={xy:.3e}")
print(f"position reassembly error: max={max(dpos):.6e} rms={rms(dpos):.6e} median={statistics.median(dpos):.6e}")
print(f"velocity reversal error  : max={max(dvel):.6e} rms={rms(dvel):.6e}")
