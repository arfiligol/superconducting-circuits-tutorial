"""
Documentation Audit Script

Checks all .md files in docs/ for compliance with guardrails:
1. Required Frontmatter fields (aliases, tags)
2. Name Validation (owner/last_updated_by must exist in contributors.md)
3. Tags Taxonomy (tags must follow namespace/value format)
"""

import os
import re

import yaml

DOCS_DIR = "docs"
CONTRIBUTORS_FILE = "docs/reference/contributors.md"

REQUIRED_FRONTMATTER = ["aliases", "tags"]
VALID_TAG_NAMESPACES = ["diataxis", "status", "audience", "topic", "sot"]


def parse_contributors():
    """Parse contributors.md to extract valid names and GitHub IDs."""
    valid_names = set()
    valid_names.add("docs-team")  # Always allow generic team names

    if not os.path.exists(CONTRIBUTORS_FILE):
        print(f"Warning: Contributors file not found: {CONTRIBUTORS_FILE}")
        return valid_names

    with open(CONTRIBUTORS_FILE, encoding="utf-8") as f:
        content = f.read()

    # Parse markdown tables - look for | Name | GitHub ID | patterns
    # Match table rows (skip header and separator rows)
    table_pattern = r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|"
    for match in re.finditer(table_pattern, content):
        name = match.group(1).strip()
        github_id = match.group(2).strip()

        # Skip header rows and empty/placeholder values
        if name in ("姓名", "Name", "---", "—", ""):
            continue
        if github_id in ("GitHub ID", "---", "—", ""):
            continue

        valid_names.add(name)
        valid_names.add(github_id)

    return valid_names


def get_frontmatter(file_path: str):
    """Extract YAML frontmatter from a markdown file."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None
    return None


def check_file(file_path: str, valid_contributors: set[str]):
    """Check a single file for compliance issues."""
    issues = []

    # Check Frontmatter
    frontmatter = get_frontmatter(file_path)
    if frontmatter is None:
        issues.append("Missing or invalid frontmatter")
    else:
        # Required fields
        for field in REQUIRED_FRONTMATTER:
            if field not in frontmatter:
                issues.append(f"Missing required field: {field}")

        # Name validation for owner and last_updated_by
        owner = frontmatter.get("owner")
        if owner and owner not in valid_contributors:
            issues.append(f"Unknown owner: '{owner}' (not in contributors.md)")

        updated_by = frontmatter.get("last_updated_by")
        if updated_by and updated_by not in valid_contributors:
            issues.append(f"Unknown last_updated_by: '{updated_by}' (not in contributors.md)")

        # Tags taxonomy validation
        tags = frontmatter.get("tags", [])
        if tags:
            for tag in tags:
                if "/" not in str(tag):
                    issues.append(f"Invalid tag format: '{tag}' (must be namespace/value)")
                else:
                    namespace = str(tag).split("/")[0]
                    if namespace not in VALID_TAG_NAMESPACES:
                        issues.append(
                            f"Invalid tag namespace: '{namespace}' "
                            f"(must be one of {VALID_TAG_NAMESPACES})"
                        )

    return issues


def main():
    # Load valid contributors
    valid_contributors = parse_contributors()
    print(f"Loaded {len(valid_contributors)} valid contributor names/IDs\n")

    # Audit all files
    report = []
    file_count = 0
    issue_count = 0

    for root, _, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                file_count += 1
                issues = check_file(file_path, valid_contributors)
                if issues:
                    report.append(f"File: {file_path}")
                    for issue in issues:
                        report.append(f"  - {issue}")
                        issue_count += 1

    # Summary
    print(f"Scanned {file_count} files, found {issue_count} issues\n")

    if report:
        print("\n".join(report))
    else:
        print("No issues found.")


if __name__ == "__main__":
    main()
