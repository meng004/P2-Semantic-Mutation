#!/bin/bash
# C-CASTRO-001 issue oracle runner (m_mono / f_mono.shape): species floor policy
# bound-preservation under true-SDC Newton update.
#
# Defect: sdc_newton_subdivide() floored the conserved species rho*X_n at the
# ABSOLUTE value network_rp::small_x instead of rho*small_x (issue #3259,
# WeiqunZhang; fixed by d9549c53 "fix small_x clamping for SDC on conserved
# state", PR #3268, zingale).
#
# Oracle: the documented floor policy is on MASS FRACTIONS: X_n >= small_x
# (Microphysics runtime parameter; this problem's shipped inputs set
# network.small_x=1e-10).  reacting_convergence initializes trace species to
# X=0 exactly, so the very first SDC Newton floor determines the trace level:
#   fixed : rho*X floored at rho*small_x  -> X_trace ~= small_x = 1e-10
#   buggy : rho*X floored at small_x      -> X_trace ~= small_x/rho ~= 2e-16
# (rho ~= 5e5 g/cc).  The sdc_order=2 path applies no other species
# normalization after the Newton update, so the floored level survives to the
# plotfile.  Judged via fextrema min of X(C12)/X(O16)/X(Fe56) [derived from
# rho*X / rho] -- min X must be >= ~small_x (fixed) vs orders below (buggy).
#
# Usage: run_and_check.sh <exec-dir> <label>
set -e
EXECDIR=$1
LABEL=$2
RUNDIR=$(pwd)/run-$LABEL
AMREX=/home/user/Defect4MR/work/castro-repro/amrex
INPUTS=$EXECDIR/inputs.64
mkdir -p $RUNDIR && cd $RUNDIR
ln -sf $EXECDIR/helm_table.dat . 2>/dev/null || true
$EXECDIR/Castro1d.gnu.TRUESDC.ex $INPUTS \
  castro.sdc_order=2 castro.time_integration_method=2 castro.ppm_type=0 \
  castro.sdc_solver=1 castro.use_retry=0 \
  max_step=5 amr.plot_int=5 amr.plot_file=plt_${LABEL}_ \
  amr.derive_plot_vars=ALL \
  > run.out 2>&1
PLT=$(ls -d plt_${LABEL}_0000[0-9] | tail -1)
echo "== $LABEL: plotfile $PLT"
$AMREX/Tools/Plotfile/fextrema.gnu.ex $PLT | grep -E "variable|rho_|X\(" || \
$AMREX/Tools/Plotfile/fextrema.gnu.ex $PLT
