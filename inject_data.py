import json
import sys

# Load JSON data
with open("latest_data.json", "r") as f:
    data = json.load(f)

# Load current index.html as raw text
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

compact = json.dumps(data, separators=(',', ':'))

# Check if already has BAKED — if so just update it
if "var BAKED=" in html:
    # Find start of BAKED
    start = html.index("var BAKED=")
    # Find the semicolon that ends this variable declaration
    # Walk forward from after "var BAKED={" to find matching closing brace + semicolon
    brace_start = html.index("{", start)
    depth = 0
    pos = brace_start
    while pos < len(html):
        if html[pos] == '{':
            depth += 1
        elif html[pos] == '}':
            depth -= 1
            if depth == 0:
                end = pos + 1  # position after closing brace
                # skip the semicolon
                if end < len(html) and html[end] == ';':
                    end += 1
                break
        pos += 1
    html = html[:start] + "var BAKED=" + compact + ";" + html[end:]
    print("Updated existing BAKED variable")

# Otherwise inject before "var D;"
elif "var D;" in html:
    pos = html.index("var D;")
    html = html[:pos] + "var BAKED=" + compact + ";\n" + html[pos:]
    print("Injected BAKED before var D;")

else:
    # Last resort: inject before </script>
    pos = html.rfind("</script>")
    if pos >= 0:
        html = html[:pos] + "\nvar BAKED=" + compact + ";\ntry{D=BAKED;}catch(e){}\n" + html[pos:]
        print("Injected BAKED before </script>")
    else:
        print("ERROR: Could not find any injection point")
        sys.exit(1)

# Write updated file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("SUCCESS: Dashboard updated")
