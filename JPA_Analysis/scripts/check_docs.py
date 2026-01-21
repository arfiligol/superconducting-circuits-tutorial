#!/usr/bin/env python3
"""
Documentation Validation Script

Validates documentation files for:
1. YAML frontmatter requirements
2. Wiki Links format and targets
3. Directory structure consistency

Usage:
    uv run python scripts/check_docs.py docs
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ============================================================================
# Constants
# ============================================================================

REQUIRED_FRONTMATTER_FIELDS = [
    "aliases",
    "tags",
    "status",
    "owner",
    "audience",
    "scope",
    "version",
    "last_updated",
    "updated_by",
]

ALLOWED_STATUS = {"draft", "review", "stable", "deprecated"}
ALLOWED_AUDIENCE = {"self", "lab", "team", "public"}
VERSION_PATTERN = re.compile(r"^v\d+\.\d+\.\d+$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WIKI_LINK_PATTERN = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class ValidationError:
    file: Path
    line: int | None
    message: str
    category: str  # "frontmatter" | "link" | "structure"


@dataclass
class ValidationResult:
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    files_checked: int = 0

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0


# ============================================================================
# Frontmatter Parsing
# ============================================================================


def parse_frontmatter(content: str) -> tuple[dict[str, str | list[str]], int]:
    """Parse YAML frontmatter from markdown content.

    Returns:
        Tuple of (frontmatter dict, end line number).
        Returns empty dict if no frontmatter found.
    """
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, 0

    end_idx = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return {}, 0

    frontmatter: dict[str, str | list[str]] = {}
    current_key: str | None = None
    current_list: list[str] = []

    for line in lines[1:end_idx]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Check for list item
        if stripped.startswith("- "):
            if current_key:
                current_list.append(stripped[2:].strip().strip('"').strip("'"))
            continue

        # Check for key-value pair
        if ":" in line:
            # Save previous list if any
            if current_key and current_list:
                frontmatter[current_key] = current_list
                current_list = []

            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if value:
                frontmatter[key] = value
                current_key = None
            else:
                current_key = key
                current_list = []

    # Save final list if any
    if current_key and current_list:
        frontmatter[current_key] = current_list

    return frontmatter, end_idx


# ============================================================================
# Validators
# ============================================================================


def validate_frontmatter(
    file_path: Path,
    content: str,
    result: ValidationResult,
) -> None:
    """Validate YAML frontmatter requirements."""
    fm, end_line = parse_frontmatter(content)

    if not fm:
        result.errors.append(
            ValidationError(
                file=file_path,
                line=1,
                message="Missing YAML frontmatter block",
                category="frontmatter",
            )
        )
        return

    # Check required fields
    for field_name in REQUIRED_FRONTMATTER_FIELDS:
        if field_name not in fm:
            result.errors.append(
                ValidationError(
                    file=file_path,
                    line=None,
                    message=f"Missing required frontmatter field: {field_name}",
                    category="frontmatter",
                )
            )

    # Validate status
    if "status" in fm:
        status = fm["status"]
        if isinstance(status, str) and status not in ALLOWED_STATUS:
            result.errors.append(
                ValidationError(
                    file=file_path,
                    line=None,
                    message=f"Invalid status '{status}'. Allowed: {ALLOWED_STATUS}",
                    category="frontmatter",
                )
            )

    # Validate audience
    if "audience" in fm:
        audience = fm["audience"]
        if isinstance(audience, str) and audience not in ALLOWED_AUDIENCE:
            result.errors.append(
                ValidationError(
                    file=file_path,
                    line=None,
                    message=f"Invalid audience '{audience}'. Allowed: {ALLOWED_AUDIENCE}",
                    category="frontmatter",
                )
            )

    # Validate version format
    if "version" in fm:
        version = fm["version"]
        if isinstance(version, str) and not VERSION_PATTERN.match(version):
            result.errors.append(
                ValidationError(
                    file=file_path,
                    line=None,
                    message=f"Invalid version format '{version}'. Expected: vX.Y.Z",
                    category="frontmatter",
                )
            )

    # Validate date format
    if "last_updated" in fm:
        date = fm["last_updated"]
        date_str = str(date) if not isinstance(date, str) else date
        if not DATE_PATTERN.match(date_str):
            result.errors.append(
                ValidationError(
                    file=file_path,
                    line=None,
                    message=f"Invalid date format '{date}'. Expected: YYYY-MM-DD",
                    category="frontmatter",
                )
            )

    # Validate tags contain required prefixes
    if "tags" in fm:
        tags = fm["tags"]
        if isinstance(tags, list):
            has_boundary = any(t.startswith("boundary/") for t in tags)
            has_audience = any(t.startswith("audience/") for t in tags)
            if not has_boundary:
                result.errors.append(
                    ValidationError(
                        file=file_path,
                        line=None,
                        message="Tags missing required 'boundary/*' tag",
                        category="frontmatter",
                    )
                )
            if not has_audience:
                result.errors.append(
                    ValidationError(
                        file=file_path,
                        line=None,
                        message="Tags missing required 'audience/*' tag",
                        category="frontmatter",
                    )
                )


def validate_wiki_links(
    file_path: Path,
    content: str,
    docs_root: Path,
    result: ValidationResult,
) -> None:
    """Validate Wiki Links format and targets."""
    lines = content.split("\n")

    for line_num, line in enumerate(lines, start=1):
        # 0. Check for unescaped pipes in links inside tables
        is_table_row = line.strip().startswith("|")

        for match in WIKI_LINK_PATTERN.finditer(line):
            link_target = match.group(1)
            link_alias = match.group(2)
            full_match = match.group(0)

            # Check for unescaped pipe in table
            if is_table_row:
                # Check if the match contains a pipe that is NOT escaped
                # Simple check: remove escaped pipes and check for remaining pipes
                content_without_escaped = full_match.replace(r"\|", "")
                if "|" in content_without_escaped:
                    result.errors.append(
                        ValidationError(
                            file=file_path,
                            line=line_num,
                            message=f"Wiki Link in table contains unescaped pipe (breaks table formatting): {full_match}. Use '\\|' or remove alias.",
                            category="link",
                        )
                    )

            # Check for missing alias
            if not link_alias:
                result.errors.append(
                    ValidationError(
                        file=file_path,
                        line=line_num,
                        message=f"Wiki Link missing alias: [[{link_target}]]",
                        category="link",
                    )
                )

            # Validate whitespace
            if link_target != link_target.strip():
                result.errors.append(
                    ValidationError(
                        file=file_path,
                        line=line_num,
                        message=f"Wiki Link target contains surrounding whitespace: '{link_target}'",
                        category="link",
                    )
                )

            clean_target = link_target.strip()

            # Resolve and check target
            target_path = resolve_wiki_link(file_path, clean_target, docs_root)
            if target_path is None:
                result.errors.append(
                    ValidationError(
                        file=file_path,
                        line=line_num,
                        message=f"Wiki Link target not found: {clean_target}",
                        category="link",
                    )
                )


def resolve_wiki_link(
    source_file: Path,
    link_target: str,
    docs_root: Path,
) -> Path | None:
    """Resolve a Wiki Link target to an actual file path."""
    # Handle docs/ prefix (absolute from docs root)
    if link_target.startswith("docs/"):
        resolved = docs_root / link_target[5:]
    # Handle relative paths
    elif link_target.startswith("./") or link_target.startswith("../"):
        resolved = (source_file.parent / link_target).resolve()
    # Handle bare names (search in same directory)
    else:
        resolved = source_file.parent / link_target

    # Check if it's a directory (needs index.md)
    if resolved.is_dir():
        index_path = resolved / "index.md"
        if index_path.exists():
            return index_path
        return None

    # Check if file exists
    if resolved.exists():
        return resolved

    # Try adding .md extension
    # IMPORTANT: Only add extension if it lacks one?
    # Or just try. But be careful of the "whitespace fix" bug.
    with_md = resolved.with_suffix(".md")
    if with_md.exists():
        return with_md

    return None


# ============================================================================
# Main Validation
# ============================================================================


def validate_file(
    file_path: Path,
    docs_root: Path,
    result: ValidationResult,
) -> None:
    """Validate a single markdown file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        result.errors.append(
            ValidationError(
                file=file_path,
                line=None,
                message=f"Failed to read file: {e}",
                category="structure",
            )
        )
        return

    result.files_checked += 1

    validate_frontmatter(file_path, content, result)
    validate_wiki_links(file_path, content, docs_root, result)


def validate_docs(docs_root: Path) -> ValidationResult:
    """Validate all markdown files in the docs directory."""
    result = ValidationResult()

    if not docs_root.exists():
        result.errors.append(
            ValidationError(
                file=docs_root,
                line=None,
                message="Documentation directory does not exist",
                category="structure",
            )
        )
        return result

    # Find all markdown files
    md_files = list(docs_root.rglob("*.md"))

    for md_file in md_files:
        validate_file(md_file, docs_root, result)

    return result


# ============================================================================
# CLI
# ============================================================================


def print_results(result: ValidationResult) -> None:
    """Print validation results to stdout."""
    if not result.errors and not result.warnings:
        print(f"✅ All {result.files_checked} files passed validation")
        return

    # Group errors by file
    errors_by_file: dict[Path, list[ValidationError]] = {}
    for error in result.errors:
        if error.file not in errors_by_file:
            errors_by_file[error.file] = []
        errors_by_file[error.file].append(error)

    for file_path, errors in sorted(errors_by_file.items()):
        print(f"\n❌ {file_path}")
        for error in errors:
            line_info = f":{error.line}" if error.line else ""
            print(f"   [{error.category}]{line_info} {error.message}")

    print(f"\n📊 Summary: {len(result.errors)} errors in {result.files_checked} files")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate documentation files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "docs_path",
        type=Path,
        help="Path to the docs directory",
    )

    args = parser.parse_args()
    docs_path: Path = args.docs_path

    if not docs_path.is_absolute():
        docs_path = Path.cwd() / docs_path

    result = validate_docs(docs_path)
    print_results(result)

    return 1 if result.has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
