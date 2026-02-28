#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

SITE_ROOT="docs/site"

./scripts/prepare_docs_locales.sh

uv run --group dev zensical build -c
uv run --group dev zensical build -f zensical.en.toml

mkdir -p "${SITE_ROOT}/en"
rm -rf "${SITE_ROOT}/en/assets" "${SITE_ROOT}/en/stylesheets" "${SITE_ROOT}/en/javascripts"
cp -a "${SITE_ROOT}/assets" "${SITE_ROOT}/en/assets"
cp -a "${SITE_ROOT}/stylesheets" "${SITE_ROOT}/en/stylesheets"
cp -a "${SITE_ROOT}/javascripts" "${SITE_ROOT}/en/javascripts"
