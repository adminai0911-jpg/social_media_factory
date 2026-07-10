import re

file_path = '.github/workflows/autopilot_server.yml'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Rename step
content = content.replace('name: Upload to 4 Platforms', 'name: Upload to 6 Platforms (Omni-Channel)')

# Inject secrets
injection = """          PINTEREST_BOARD_ID: ${{ secrets.PINTEREST_BOARD_ID }}
          PINTEREST_ACCESS_TOKEN: ${{ secrets.PINTEREST_ACCESS_TOKEN }}
          LINKEDIN_ACCESS_TOKEN: ${{ secrets.LINKEDIN_ACCESS_TOKEN }}
          LINKEDIN_AUTHOR_URN: ${{ secrets.LINKEDIN_AUTHOR_URN }}"""

content = content.replace('          PINTEREST_BOARD_ID: ${{ secrets.PINTEREST_BOARD_ID }}', injection)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Workflow patched.")
