"""
Generate Bilingual Stubs Script

Creates .en.md stub files for all .md files that lack an English counterpart.
Copies frontmatter from source and adds placeholder content.
"""

import os
import re

DOCS_DIR = "docs"

STUB_CONTENT_TEMPLATE = (
    "> **Note**: This document is pending translation. "
    "Please refer to the\n"
    "> [Traditional Chinese version]({zh_filename}).\n\n"
    "---\n\n"
    "{original_title}\n"
)


def get_frontmatter_and_title(file_path):
    """Extract frontmatter and title from source file."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    frontmatter = ""
    title = "# Untitled"

    # Extract frontmatter
    match = re.match(r"^(---\n.*?\n---)", content, re.DOTALL)
    if match:
        frontmatter = match.group(1)
        rest = content[match.end() :]
    else:
        rest = content

    # Extract title
    title_match = re.search(r"^(#\s+.+)$", rest, re.MULTILINE)
    if title_match:
        title = title_match.group(1)

    return frontmatter, title


def generate_stub(source_path, target_path):
    """Generate an English stub file."""
    frontmatter, title = get_frontmatter_and_title(source_path)

    # Get relative filename for link
    zh_filename = os.path.basename(source_path)

    # Generate stub content
    stub_content = STUB_CONTENT_TEMPLATE.format(zh_filename=zh_filename, original_title=title)

    # Combine frontmatter and stub content
    full_content = (frontmatter + "\n" + stub_content) if frontmatter else stub_content

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(full_content)

    return True


def main():
    created_count = 0
    skipped_count = 0

    for root, _, files in os.walk(DOCS_DIR):
        for file in files:
            # Only process Chinese source files (not .en.md)
            if file.endswith(".md") and not file.endswith(".en.md"):
                source_path = os.path.join(root, file)
                target_path = source_path.replace(".md", ".en.md")

                # Check if English version already exists
                if os.path.exists(target_path):
                    skipped_count += 1
                    continue

                # Generate stub
                generate_stub(source_path, target_path)
                print(f"Created: {target_path}")
                created_count += 1

    print(f"\nSummary: Created {created_count} stubs, Skipped {skipped_count} (already exist)")


if __name__ == "__main__":
    main()
