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

# Strategy 1: Replace existing BAKED variable (multiline)
pattern1 = r'var BAKED=\{[\s\S]*?\};(\s*\n)var D;'
if re.search(pattern1, html):
    html = re.sub(pattern1, 'var BAKED=' + compact + ';\\1var D;', html)
    print("Strategy 1: Replaced existing BAKED variable")
    injected = True

# Strategy 2: Replace one-liner BAKED
elif re.search(r'var BAKED=\{[^;]+\};', html):
    html = re.sub(r'var BAKED=\{[^;]+\};', 'var BAKED=' + compact + ';', html)
    print("Strategy 2: Replaced one-liner BAKED")
    injected = True

# Strategy 3: Original LD block with DEF
elif "JSON.stringify(DEF)" in html and "function LD(){" in html:
    old = "var D;\nfunction LD(){try{var s=localStorage.getItem('lp6');return s?JSON.parse(s):JSON.parse(JSON.stringify(DEF));}catch(e){return JSON.parse(JSON.stringify(DEF));}}\nD=LD();"
    new = "var BAKED=" + compact + ";\nvar D;\nfunction LD(){try{var s=localStorage.getItem('lp6');return s?JSON.parse(s):JSON.parse(JSON.stringify(BAKED));}catch(e){return JSON.parse(JSON.stringify(BAKED));}}\nD=LD();"
    if old in html:
        html = html.replace(old, new)
        print("Strategy 3: Injected into original LD block")
        injected = True

# Strategy 4: Already has BAKED in LD
elif "JSON.stringify(BAKED)" in html and "var D;" in html:
    html = re.sub(r'var BAKED=[^;]+;', 'var BAKED=' + compact + ';', html)
    print("Strategy 4: Updated BAKED in modified LD block")
    injected = True

# Strategy 5: Fallback - inject before var D;
elif "var D;" in html:
    html = html.replace("var D;", "var BAKED=" + compact + ";\nvar D;", 1)
    print("Strategy 5: Injected before var D;")
    injected = True

if not injected:
    print("ERROR: Could not find injection point in HTML")
    sys.exit(1)

# Write updated file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("SUCCESS: Dashboard updated and ready to push")
