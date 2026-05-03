#!/usr/bin/env bash
# build_zip.sh — produce replication.zip for Zenodo upload.
#
# Filter rules:
#   INCLUDE: src/, scripts/, tests/, replication/, requirements-frozen.txt,
#            README.md, REPRODUCIBILITY.md, DATASET.md, ZENODO.md, LICENSE,
#            paper files (CN/EN/IST/appendix), figures/, data/results/*.json
#            (only those <=500 KB), data/results/cosmic_ray_*_summary.json,
#            data/results/cosmic_ray_*.sqlite (only those <5 MB),
#            data/mutants/*_pool_v4/, docs/review_2026-05-{01,02}/,
#            .cr-*.toml configs, configs/, src .env.example.
#   EXCLUDE: .git/, .venv/, .translate_cache/, .claude/, .pytest_cache/,
#            .superpowers/, submission/texmf/, *.aux/*.log/*.pyc,
#            __pycache__/, large pickles, raw API logs
#            (data/operator_campaign/raw/), sqlite >5 MB, .DS_Store,
#            .env, large unused mutant pools (_pool, _pool_v3, _pool_v3b,
#            _MP*_llm, _MP*_mut1).

set -euo pipefail

# Resolve project root (directory above this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

OUT_ZIP="${SCRIPT_DIR}/replication.zip"
STAGING="$(mktemp -d -t p2_zenodo_stage_XXXXXX)"
PKG_NAME="p2-sms-replication-v1.0.0"
PKG_DIR="${STAGING}/${PKG_NAME}"
mkdir -p "${PKG_DIR}"

trap 'rm -rf "${STAGING}"' EXIT

echo "[1/6] Staging directory: ${PKG_DIR}"

# --------------------------------------------------------------------------
# 1. Top-level files
# --------------------------------------------------------------------------
for f in \
  README.md REPRODUCIBILITY.md DATASET.md ZENODO.md LICENSE \
  requirements-frozen.txt pyproject.toml .python-version .env.example \
  AGENTS.md \
  论文初稿P2.md 论文初稿P2_EN.md 论文初稿P2_IST.md 论文初稿P2_IST_appendix.md
do
  if [[ -f "${f}" ]]; then
    mkdir -p "${PKG_DIR}/$(dirname "${f}")"
    cp "${f}" "${PKG_DIR}/${f}"
  fi
done

# Cosmic-ray TOML configs
for f in .cr-*.toml; do
  [[ -f "${f}" ]] && cp "${f}" "${PKG_DIR}/"
done

# --------------------------------------------------------------------------
# 2. Source code, scripts, tests, configs
# --------------------------------------------------------------------------
echo "[2/6] Copying src/, scripts/, tests/, configs/"
rsync -a \
  --exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' \
  --exclude='.DS_Store' --exclude='*.egg-info' \
  src/ "${PKG_DIR}/src/"

rsync -a \
  --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
  scripts/ "${PKG_DIR}/scripts/"

rsync -a \
  --exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' \
  --exclude='.DS_Store' \
  tests/ "${PKG_DIR}/tests/"

if [[ -d configs ]]; then
  rsync -a --exclude='.DS_Store' configs/ "${PKG_DIR}/configs/"
fi

# --------------------------------------------------------------------------
# 3. Replication metadata (this directory)
# --------------------------------------------------------------------------
echo "[3/6] Copying replication/"
rsync -a \
  --exclude='replication.zip' --exclude='MANIFEST.txt' --exclude='.DS_Store' \
  replication/ "${PKG_DIR}/replication/"

# --------------------------------------------------------------------------
# 4. Selected data
#    - data/results/*.json with size <= 500 KB
#    - data/results/cosmic_ray_*_summary.json (always)
#    - data/results/cosmic_ray_*.sqlite with size < 5 MB
#    - data/results/*.log, *.txt console artefacts
#    - data/mutants/*_pool_v4/ (12 directories)
# --------------------------------------------------------------------------
echo "[4/6] Copying selected data/"
mkdir -p "${PKG_DIR}/data/results"

# JSON results: include if <= 500 KB (uses BSD/GNU compatible find)
find data/results -maxdepth 1 -name '*.json' -size -512k -print0 \
  | while IFS= read -r -d '' f; do
      cp "${f}" "${PKG_DIR}/${f}"
    done

# Always include cosmic_ray_*_summary.json (small) — already covered above,
# but be defensive in case a summary later exceeds 500 KB
find data/results -maxdepth 1 -name 'cosmic_ray_*_summary.json' -print0 \
  | while IFS= read -r -d '' f; do
      cp "${f}" "${PKG_DIR}/${f}"
    done

# Cosmic-ray sqlite: include if < 5 MB
find data/results -maxdepth 1 -name 'cosmic_ray_*.sqlite' -size -5120k -print0 \
  | while IFS= read -r -d '' f; do
      cp "${f}" "${PKG_DIR}/${f}"
    done

# Console logs and concurrency probe (small, audit-relevant)
find data/results -maxdepth 1 \( -name '*.log' -o -name '*.txt' \) -size -512k -print0 \
  | while IFS= read -r -d '' f; do
      cp "${f}" "${PKG_DIR}/${f}"
    done

# Operator-campaign log only (the v2_revised6.log audit trail)
mkdir -p "${PKG_DIR}/data/operator_campaign"
if [[ -f data/operator_campaign/v2_revised6.log ]]; then
  cp data/operator_campaign/v2_revised6.log \
     "${PKG_DIR}/data/operator_campaign/v2_revised6.log"
fi

# Mutant pools: only *_pool_v4 (paper-cited primary)
mkdir -p "${PKG_DIR}/data/mutants"
for d in data/mutants/*_pool_v4; do
  if [[ -d "${d}" ]]; then
    rsync -a --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
      "${d}" "${PKG_DIR}/data/mutants/"
  fi
done

# --------------------------------------------------------------------------
# 5. Reviewer reports + figures + submission artifacts
# --------------------------------------------------------------------------
echo "[5/6] Copying docs/review_*, figures/, submission/"
mkdir -p "${PKG_DIR}/docs"
for d in docs/review_2026-05-01 docs/review_2026-05-02; do
  if [[ -d "${d}" ]]; then
    rsync -a --exclude='.DS_Store' "${d}/" "${PKG_DIR}/${d}/"
  fi
done

if [[ -d figures ]]; then
  rsync -a --exclude='.DS_Store' figures/ "${PKG_DIR}/figures/"
fi

# Submission artifacts (cover letter, PDF, process summaries) — exclude texmf/ and TeX intermediates
mkdir -p "${PKG_DIR}/submission"
if [[ -d submission ]]; then
  rsync -a \
    --exclude='texmf/' --exclude='*.aux' --exclude='*.log' --exclude='*.out' \
    --exclude='*.spl' --exclude='.DS_Store' \
    submission/ "${PKG_DIR}/submission/"
fi

# --------------------------------------------------------------------------
# 6. Generate MANIFEST.txt (alphabetically sorted, SHA256 + size)
# --------------------------------------------------------------------------
echo "[6/6] Generating MANIFEST.txt"
MANIFEST="${PKG_DIR}/replication/MANIFEST.txt"
{
  echo "# Replication package manifest — ${PKG_NAME}"
  echo "# Format: SHA256  SIZE_BYTES  RELATIVE_PATH"
  echo "# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ) by build_zip.sh"
  echo "#"
  cd "${PKG_DIR}"
  # shasum is on macOS; sha256sum on Linux. Try shasum first.
  if command -v shasum >/dev/null 2>&1; then
    HASHER='shasum -a 256'
  else
    HASHER='sha256sum'
  fi
  find . -type f ! -name 'MANIFEST.txt' -print0 \
    | LC_ALL=C sort -z \
    | while IFS= read -r -d '' f; do
        size=$(wc -c < "${f}" | tr -d ' ')
        hash=$(${HASHER} "${f}" | awk '{print $1}')
        # strip leading "./"
        rel="${f#./}"
        echo "${hash}  ${size}  ${rel}"
      done
} > "${MANIFEST}"

# Also copy the manifest back to the working replication/ dir for convenience
cp "${MANIFEST}" "${SCRIPT_DIR}/MANIFEST.txt"

# --------------------------------------------------------------------------
# 7. Build the zip
# --------------------------------------------------------------------------
echo "[zip] Creating ${OUT_ZIP}"
rm -f "${OUT_ZIP}"
( cd "${STAGING}" && zip -rq "${OUT_ZIP}" "${PKG_NAME}" -x '*.DS_Store' )

# --------------------------------------------------------------------------
# 8. Size summary + Zenodo soft-limit check (500 MB)
# --------------------------------------------------------------------------
SIZE_BYTES=$(wc -c < "${OUT_ZIP}" | tr -d ' ')
SIZE_MB=$(awk -v b="${SIZE_BYTES}" 'BEGIN { printf "%.2f", b/1024/1024 }')

echo
echo "================================================================"
echo " Replication package built"
echo "----------------------------------------------------------------"
echo " Zip:          ${OUT_ZIP}"
echo " Size:         ${SIZE_MB} MB (${SIZE_BYTES} bytes)"
echo " Manifest:     ${SCRIPT_DIR}/MANIFEST.txt"
echo " File count:   $(find "${PKG_DIR}" -type f | wc -l | tr -d ' ')"
echo "================================================================"

LIMIT_MB=500
if awk -v s="${SIZE_MB}" -v l="${LIMIT_MB}" 'BEGIN { exit !(s > l) }'; then
  echo "ERROR: zip size ${SIZE_MB} MB exceeds Zenodo soft limit ${LIMIT_MB} MB."
  echo "       Trim further (e.g., remove cosmic_ray_*.sqlite, more pools)."
  exit 1
fi
echo "OK: under Zenodo ${LIMIT_MB} MB soft limit."
