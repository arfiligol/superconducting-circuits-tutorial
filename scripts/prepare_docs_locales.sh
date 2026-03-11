#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

DOCS_ROOT="docs"
ZH_DOCS_DIR="${DOCS_ROOT}/docs_zhtw"

rm -rf "${ZH_DOCS_DIR}"

rsync -a --delete \
  --exclude "docs_zhtw/" \
  --exclude "site/" \
  "${DOCS_ROOT}/" "${ZH_DOCS_DIR}/"

find "${ZH_DOCS_DIR}" -depth -type f -name "*.en.md" -exec sh -c '
for path do
  target="${path%.en.md}.md"
  if [ -e "${target}" ]; then
    rm "${path}"
  else
    mv "${path}" "${target}"
  fi
done
' sh {} +
