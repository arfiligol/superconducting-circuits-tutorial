#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

rm -rf docs_zh docs_en

cp -a docs docs_zh
find docs_zh -depth -type f -name "*.en.md" -exec sh -c '
for path do
  target="${path%.en.md}.md"
  if [ -e "${target}" ]; then
    rm "${path}"
  else
    mv "${path}" "${target}"
  fi
done
' sh {} +

cp -a docs docs_en
find docs_en -depth -type f -name "*.en.md" -exec sh -c '
for path do
  mv "${path}" "${path%.en.md}.md"
done
' sh {} +
