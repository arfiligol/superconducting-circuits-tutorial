"""
Fix Frontmatter Script

Adds missing frontmatter to files that lack it.
Generates default aliases (from title or filename) and tags (from directory path).
"""

import os
import re

DOCS_DIR = "docs"


def get_title_from_content(content):
    """Extract H1 title from markdown content."""
    # Look for first H1
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def infer_diataxis_type(file_path):
    """Infer diataxis type from directory path."""
    if "/tutorials/" in file_path:
        return "diataxis/tutorial"
    elif "/how-to/" in file_path:
        return "diataxis/how-to"
    elif "/reference/" in file_path:
        return "diataxis/reference"
    elif "/explanation/" in file_path:
        return "diataxis/explanation"
    elif "/notebooks/" in file_path:
        return "diataxis/reference"  # Notebooks are reference material
    return "diataxis/reference"  # Default


def infer_topic(file_path):
    """Infer topic from directory path."""
    if "/simulation/" in file_path:
        return "topic/simulation"
    elif "/analysis/" in file_path:
        return "topic/analysis"
    elif "/physics/" in file_path:
        return "topic/physics"
    elif "/cli/" in file_path:
        return "topic/cli"
    elif "/data-formats/" in file_path:
        return "topic/data-format"
    elif "/guardrails/" in file_path:
        return "topic/governance"
    elif "/getting-started/" in file_path:
        return "topic/getting-started"
    elif "/preprocess/" in file_path:
        return "topic/preprocessing"
    elif "/contributing/" in file_path:
        return "topic/contributing"
    elif "/extend/" in file_path:
        return "topic/extension"
    elif "/architecture/" in file_path:
        return "topic/architecture"
    return None


def generate_frontmatter(file_path, content):
    """Generate default frontmatter for a file."""
    # Get title
    title = get_title_from_content(content)
    if not title:
        # Use filename as fallback
        filename = os.path.basename(file_path).replace(".md", "").replace(".en", "")
        title = filename.replace("-", " ").title()

    # Build aliases
    aliases = [title]

    # Build tags
    tags = []

    # Diataxis type
    diataxis = infer_diataxis_type(file_path)
    tags.append(diataxis)

    # Status (default to draft for missing frontmatter)
    tags.append("status/draft")

    # Topic
    topic = infer_topic(file_path)
    if topic:
        tags.append(topic)

    # Build YAML
    aliases_yaml = "\n".join([f'  - "{a}"' for a in aliases])
    tags_yaml = "\n".join([f"  - {t}" for t in tags])

    frontmatter = f"""---
aliases:
{aliases_yaml}
tags:
{tags_yaml}
---
"""
    return frontmatter


def fix_frontmatter_in_file(file_path):
    """Add frontmatter to a file if missing."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Check if file already has frontmatter
    if content.strip().startswith("---"):
        # Has frontmatter, check if valid
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            return False, "Already has valid frontmatter"

    # Generate and add frontmatter
    frontmatter = generate_frontmatter(file_path, content)
    new_content = frontmatter + "\n" + content.lstrip()

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True, "Added frontmatter"


def main():
    fixed_count = 0
    skipped_count = 0

    for root, _, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)

                success, _message = fix_frontmatter_in_file(file_path)
                if success:
                    print(f"Fixed: {file_path}")
                    fixed_count += 1
                else:
                    skipped_count += 1

    print(f"\nSummary: Fixed {fixed_count} files, Skipped {skipped_count} files")


if __name__ == "__main__":
    main()
