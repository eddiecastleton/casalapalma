import requests
import json
import sys

FILE_ID = "1em42hJywm5s41FTKtQahmoDwJgoXW5LN"

url = "https://drive.google.com/uc?export=download&id=" + FILE_ID
session = requests.Session()
response = session.get(url, allow_redirects=True)

# Handle Google virus scan warning for larger files
if "confirm=" in response.text or "download_warning" in response.text:
    import re
    confirm = re.search(r'confirm=([0-9A-Za-z_]+)', response.text)
    if confirm:
        url = "https://drive.google.com/uc?export=download&id=" + FILE_ID + "&confirm=" + confirm.group(1)
        response = session.get(url)

with open("latest_data.json", "wb") as f:
    f.write(response.content)

# Validate
with open("latest_data.json", "r") as f:
    data = json.load(f)

if not data.get("cfg") or not data.get("contractors"):
    print("ERROR: Not a valid Casa La Palma backup file")
    sys.exit(1)

print("SUCCESS: Downloaded JSON - " + str(len(data.get("contractors", []))) + " contractors, " + str(len(data.get("phases", []))) + " phases, " + str(len(data.get("tasks", []))) + " tasks")
