import sys
import re

with open('uploader.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add imports
imports_to_add = """from linkedin_uploader import upload_to_linkedin
from pinterest_uploader import upload_to_pinterest
"""

code = code.replace('import json', 'import json\n' + imports_to_add)

# Find the distribute_to_all_platforms function
# We will inject the LinkedIn and Pinterest calls before sending the Telegram alert

injection = """
    # ── LINKEDIN ──
    try:
        li = upload_to_linkedin(video_path, injected_description)
    except Exception as e:
        logger.error(f"LinkedIn Exception: {e}")
        li = False

    # ── PINTEREST ──
    try:
        pin = upload_to_pinterest(video_path, injected_description)
    except Exception as e:
        logger.error(f"Pinterest Exception: {e}")
        pin = False
"""

code = code.replace('    # ── SEND TELEGRAM FINAL STATUS MESSAGE ──', injection + '\n    # ── SEND TELEGRAM FINAL STATUS MESSAGE ──')

# Update the status message
old_status = """<b>Buffer Bridge (Pinterest / LinkedIn):</b>
🚀 Make.com Webhook: {'✅' if buffer_bridge else '❌'}"""

new_status = """<b>Direct API Integrations (New Handler):</b>
💼 LinkedIn Profile: {'✅' if li else '❌'}
📌 Pinterest Board: {'✅' if pin else '❌'}
🚀 Make.com Webhook (Legacy): {'✅' if buffer_bridge else '❌'}"""

code = code.replace(old_status, new_status)

# Update return dict
old_return = """        "ig_story": ig_story,
        "buffer_bridge": buffer_bridge
    }"""
new_return = """        "ig_story": ig_story,
        "buffer_bridge": buffer_bridge,
        "linkedin": li,
        "pinterest": pin
    }"""
code = code.replace(old_return, new_return)

with open('uploader.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("uploader.py patched successfully.")
