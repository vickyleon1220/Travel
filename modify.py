import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Change seats for f1
# Find the seats block for f1 and replace
# Pattern: from "seats: {" up to the closing "}" after Honn: '4A'
# We'll use a regex that captures the whole seats block for f1.
def replace_seats_f1(m):
    # m.group(0) is the whole match
    # We'll replace the inner lines
    return '''        seats: {
          James: '34H',
          Vicky: '33H',
          Chenn: '33K',
          Honn: '34K'
        }'''

# Use re.DOTALL to match across lines.
pattern = r'(id: \'f1\'[^}]*?seats: \{)[\s\S]*?(\})'
content = re.sub(pattern, lambda m: m.group(1) + '\n          James: \'34H\',\n          Vicky: \'33H\',\n          Chenn: \'33K\',\n          Honn: \'34K\'\n        }', content, flags=re.DOTALL)

# 2. Remove hsr tab from translation dict (zh and en)
# We'll remove the line containing hsr: '...' inside the tabs object.
# We'll do it by removing the line and ensuring we don't leave trailing commas.
lines = content.splitlines()
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    # Detect entering zh or en block
    if stripped.startswith('zh:') or stripped.startswith('en:'):
        # We'll just copy lines until we exit the block? Simpler: remove hsr line wherever it appears inside tabs.
        # We'll just skip lines that start with hsr: and are inside a tabs block.
        # We'll need to know if we are inside tabs.
        pass
    new_lines.append(line)
    i += 1

# Instead, we can do a regex removal for the hsr line inside tabs.
# We'll replace pattern: tabs: { ... hsr: '...', ... } with tabs: { ... ... } removing the hsr line.
# We'll do for both zh and en.
def remove_hsr_from_tabs_block(block):
    # block is the content inside tabs: { ... }
    # Remove the hsr line and any trailing comma before it.
    lines_block = block.split('\n')
    new_block_lines = []
    for ln in lines_block:
        if ln.strip().startswith('hsr:'):
            # skip this line
            # Also, if previous line ends with a comma, we might need to remove that comma to avoid double comma.
            # We'll handle later by rejoining and cleaning.
            continue
        new_block_lines.append(ln)
    # Join and clean up trailing commas before closing brace
    new_block = '\n'.join(new_block_lines)
    # Replace pattern of a comma followed by whitespace* and then } with just }
    new_block = re.sub(r',\s*(\})', r'\1', new_block)
    return new_block

# We'll do a more robust approach: find the tabs object for zh and en and replace.
# Use regex to find zh: { ... tabs: { ... } ... } and en: { ... tabs: { ... } ... }
def replace_tabs(content, lang):
    # pattern to capture the language block up to the next language or end of dict
    # We'll use a regex that matches from lang: { up to the next }, but careful with nested braces.
    # Simpler: we can just remove hsr line globally if it's inside tabs: { ... }.
    # We'll do a regex that matches inside tabs: { ... } and removes hsr line.
    # pattern: (tabs:\s*\{[\s\S]*?)hsr:\s*[^}]*?([\s\S]*?\})
    # We'll replace with \1\2
    pattern = rf'({lang}:\s*\{[\s\S]*?tabs:\s*\{\s*)[\s\S]*?hsr:\s*[\'"][^\'"]*[\'"],?[\s\S]*?(\}[\s\S]*?\})'
    # This is getting complex.
    # Let's instead do line-by-line with state.
    return content

# Given time, we'll do a simpler approach: remove the hsr line from the dict wherever it appears, and also remove the comma if it causes double comma.
# We'll just delete lines that contain hsr: and are inside the dict (we can assume they are only in the tabs object).
# We'll also need to remove the corresponding entries in en dict.
# Let's just do two passes: remove hsr line from zh and en sections.

# We'll split by lines and keep track of whether we are inside zh or en and inside tabs.
lines = content.splitlines()
new_lines = []
in_zh = False
in_en = False
in_tabs_zh = False
in_tabs_en = False
for line in lines:
    stripped = line.strip()
    if stripped.startswith('zh:'):
        in_zh = True
        in_en = False
        in_tabs_zh = False
        in_tabs_en = False
    elif stripped.startswith('en:'):
        in_en = True
        in_zh = False
        in_tabs_zh = False
        in_tabs_en = False
    elif in_zh and stripped.startswith('tabs:'):
        in_tabs_zh = True
        in_tabs_en = False
    elif in_en and stripped.startswith('tabs:'):
        in_tabs_en = True
        in_tabs_zh = False
    # If we are inside tabs and line starts with hsr:, skip it
    if (in_tabs_zh or in_tabs_en) and stripped.startswith('hsr:'):
        # Skip this line; also we need to possibly remove a trailing comma from previous line if it ends with comma and this line is removed.
        # We'll handle by checking the last line in new_lines: if it ends with a comma, we can remove that comma.
        # But we also need to consider that there might be a comma after hsr line (since it's inside an object).
        # The hsr line itself ends with a comma (since it's not the last entry). We'll skip the whole line.
        # To avoid double commas, we can check if the previous line in new_lines ends with a comma and the next line (after skipping) also starts with something that might cause double comma.
        # Simpler: we'll just skip and later we can clean up double commas with a regex.
        continue
    new_lines.append(line)

content = '\n'.join(new_lines)

# Clean up possible double commas: replace ',,,' with ',' and also ',\s*,' with ','
content = re.sub(r',\s*,', ',', content)

# 3. Remove the HSR tab button UI
# Remove the button with onClick={() => setActiveTab('hsr')}
# We'll remove the whole button element.
# Pattern: <button ... onClick={() => setActiveTab('hsr')} ... > ... </button>
content = re.sub(r'<button\s+[^>]*onClick=\{\(\) => setActiveTab\(\'hsr\'\)\}[^>]*>[\s\S]*?</button>', '', content, flags=re.DOTALL)

# 4. Remove the HSR tab heading (likely <h2>🚄 {t.tabs.hsr}</h2>)
content = re.sub(r'<h2[^>]*>\s*🚄\s*\{t\.tabs\.hsr\}\s*</h2>', '', content, flags=re.DOTALL)

# Also remove any lingering hsr references in the dict? We already removed hsr from tabs.

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
