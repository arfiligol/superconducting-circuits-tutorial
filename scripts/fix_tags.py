import os
import re

import yaml

DOCS_DIR = "docs"


def get_frontmatter(content):
    match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1)), match.span()
        except yaml.YAMLError:
            return None, None
    return None, None


def remove_boundary_tags(file_path):
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    frontmatter, span = get_frontmatter(content)
    if not frontmatter or not span:
        print(f"Skipping {file_path}: Invalid/No frontmatter")
        return False

    tags = frontmatter.get("tags", [])
    if not tags:
        return False

    # Filter out boundary tags
    new_tags = [tag for tag in tags if not str(tag).startswith("boundary/")]

    if len(tags) == len(new_tags):
        return False  # No changes

    print(f"Fixing {file_path}: Removing {len(tags) - len(new_tags)} boundary tags")

    # Update frontmatter
    frontmatter["tags"] = new_tags

    # Dump YAML (try to keep clean format)
    new_yaml = yaml.dump(
        frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False
    ).strip()

    # Reconstruct content
    new_content = f"---\n{new_yaml}\n---{content[span[1] :]}"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


def main():
    modified_count = 0
    for root, _, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                if remove_boundary_tags(file_path):
                    modified_count += 1

    print(f"\nCompleted! Modified {modified_count} files.")


if __name__ == "__main__":
    main()
