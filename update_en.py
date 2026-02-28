import re

with open('zensical.en.yml', 'r') as f:
    config = f.read()

# Replace site_name and URL
config = re.sub(r'site_name:.*', 'site_name: Superconducting Circuits Tutorial', config)
config = re.sub(r'site_url:.*', 'site_url: https://arfiligol.github.io/superconducting-circuits-tutorial/en/', config)

# Add docs_dir and site_dir after repo_name
config = re.sub(r'(repo_name: arfiligol/superconducting-circuits-tutorial)', r'\1\n\ndocs_dir: docs_en\nsite_dir: site/en', config)

# Add theme language
config = re.sub(r'(theme:\n  name: zensical\n  custom_dir: overrides)', r'\1\n  language: en', config)

# Remove the i18n plugin block completely
# Matches "- i18n" block until the empty line before markdown_extensions
config = re.sub(r'  - i18n:.*?(?=\n\nmarkdown_extensions:)', '', config, flags=re.DOTALL)

with open('zensical.en.yml', 'w') as f:
    f.write(config)
