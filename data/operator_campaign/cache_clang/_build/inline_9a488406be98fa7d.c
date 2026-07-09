```c
/* B2: MCMC Metropolis-Hastings - chain mean tracking target (scalar x in [0,1]).
 *
 * C99 port of src/p2/puts/b2.py. Target N(mu,1), mu = 4x-2. MH from
 * x0=0, n_steps=2000, warmup=500, proposal_std=0.5. Returns post-warmup
 * chain mean.
 *
 * RNG CONTRACT: the Python reference draws from numpy PCG64
 * (default_rng(42)); numpy's exact bit-stream cannot be reproduced in
 * C99. This port embeds a deterministic 64-bit LCG (seed 42) with
 * Box-Muller normals. The contract is DISTRIBUTIONAL EQUIVALENCE (the
 * post-warmup chain mean tracks mu to within MCMC error), NOT bit-for-bit
 * equality with the Python value. Both the C original and every C mutant
 * share this same fixed seed, so intra-C comparisons remain deterministic.
 *
 * Pure C99 + libm.
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static const int    N_STEPS = 2000;
static const int    WARMUP  = 500;
static const double PROPOSAL_STD = 0.5;
static const unsigned long long SEED = 42ULL;

static unsigned long long rng_state;
static void   rng_seed(unsigned long long s) { rng_state = s ? s : 0x9E3779B97F4A7C15ULL; }
static double u01(void) {
    rng_state =