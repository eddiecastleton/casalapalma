import json
import re
import sys

# Load JSON data
with open("latest_data.json", "r") as f:
    data = json.load(f)

# Load current index.html
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

compact = json.dumps(data, separators=(',', ':'))
injected = False

# Strategy 1: Already has BAKED variable — just replace the value
if "var BAKED=" in html:
    html = re.sub(r'var BAKED=\{[\s\S]*?\};', 'var BAKED=' + compact + ';', html, count=1)
    print("Strategy 1: Replaced existing BAKED variable")
    injected = True

# Strategy 2: Original single-line LD block (matches actual GitHub file format)
elif "var D;\nfunction LD(){" in html and "JSON.stringify(DEF)" in html:
    old = "var D;\nfunction LD(){try{var s=localStorage.getItem('lp6');return s?JSON.parse(s):JSON.parse(JSON.stringify(DEF));}catch(e){return JSON.parse(JSON.stringify(DEF));}}\nD=LD();"
    new = "var BAKED=" + compact + ";\nvar D;\nfunction LD(){try{var s=localStorage.getItem('lp6');return s?JSON.parse(s):JSON.parse(JSON.stringify(BAKED));}catch(e){return JSON.parse(JSON.stringify(BAKED));}}\nD=LD();"
    if old in html:
        html = html.replace(old, new)
        print("Strategy 2: Replaced original LD block")
        injected = True

# Strategy 3: Find var D; and LD on same or adjacent lines using regex
if not injected:
    pattern = r'var D;\s*\nfunction LD\(\)\{[^\n]+\}\s*\nD=LD\(\);'
    if re.search(pattern, html):
        replacement = "var BAKED=" + compact + ";\nvar D;\nfunction LD(){try{var s=localStorage.getItem('lp6');return s?JSON.parse(s):JSON.parse(JSON.stringify(BAKED));}catch(e){return JSON.parse(JSON.stringify(BAKED));}}\nD=LD();"
        html = re.sub(pattern, replacement, html, count=1)
        print("Strategy 3: Replaced LD block via regex")
        injected = True

# Strategy 4: Just find var D; and inject BAKED before it
if not injected and "var D;" in html:
    html = html.replace("var D;", "var BAKED=" + compact + ";\nvar D;", 1)
    print("Strategy 4: Injected BAKED before var D;")
    injected = True

if not injected:
    print("ERROR: Could not find injection point in HTML")
    sys.exit(1)

# Write updated file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("SUCCESS: Dashboard updated and ready to push")
