#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

./scripts/prepare_docs_locales.sh

uv run --group dev zensical build -c
uv run --group dev zensical build -f zensical.en.toml

mkdir -p site/en
rm -rf site/en/assets site/en/stylesheets site/en/javascripts
cp -a site/assets site/en/assets
cp -a site/stylesheets site/en/stylesheets
cp -a site/javascripts site/en/javascripts
