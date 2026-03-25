import json
import sys

# Load JSON data
with open("latest_data.json", "r") as f:
    data = json.load(f)

# Load current index.html
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

compact = json.dumps(data, separators=(',', ':'))

# ── Step 1: Inject or update BAKED variable ──
if "var BAKED=" in html:
    # Already has BAKED — update the value
    start = html.index("var BAKED=")
    brace_start = html.index("{", start)
    depth = 0
    pos = brace_start
    while pos < len(html):
        if html[pos] == '{':
            depth += 1
        elif html[pos] == '}':
            depth -= 1
            if depth == 0:
                end = pos + 1
                if end < len(html) and html[end] == ';':
                    end += 1
                break
        pos += 1
    html = html[:start] + "var BAKED=" + compact + ";" + html[end:]
    print("Step 1: Updated existing BAKED variable")
elif "var D;" in html:
    pos = html.index("var D;")
    html = html[:pos] + "var BAKED=" + compact + ";\n" + html[pos:]
    print("Step 1: Injected BAKED before var D;")
else:
    print("ERROR: Could not find injection point")
    sys.exit(1)

# ── Step 2: Fix LD function to use BAKED not DEF ──
# This is the critical fix — makes the public dashboard always show BAKED data
old_ld = "function LD(){try{var s=localStorage.getItem('lp6');return s?JSON.parse(s):JSON.parse(JSON.stringify(DEF));}catch(e){return JSON.parse(JSON.stringify(DEF));}}"
new_ld = "function LD(){try{var s=localStorage.getItem('lp6');return s?JSON.parse(s):JSON.parse(JSON.stringify(BAKED));}catch(e){return JSON.parse(JSON.stringify(BAKED));}}"

if old_ld in html:
    html = html.replace(old_ld, new_ld)
    print("Step 2: Fixed LD function to use BAKED instead of DEF")
elif "JSON.stringify(BAKED)" in html:
    print("Step 2: LD function already using BAKED - no change needed")
else:
    print("WARNING: Could not update LD function - data may not display correctly")

# ── Step 3: Write updated file ──
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("SUCCESS: Dashboard updated and ready to push")
