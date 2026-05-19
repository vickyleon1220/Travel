import re

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Update seats for f1
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Look for start of f1 object
    if '"id": \'f1\'"' in line or "id: 'f1'" in line:
        # We'll keep this line and continue until we find the seats block
        new_lines.append(line)
        i += 1
        # Continue until we hit the seats line
        while i < len(lines) and not lines[i].strip().startswith('seats:'):
            new_lines.append(lines[i])
            i += 1
        # Now we are at the seats line
        # Replace the seats block with new content
        new_lines.append('        seats: {\n')
        i += 1  # skip the old seats: {
        # skip the four seat lines
        # We expect exactly four lines for James, Vicky, Chenn, Honn
        # We'll skip until we pass the Honn line
        while i < len(lines) and not lines[i].strip().startswith('},'):
            # If line starts with James, Vicky, Chenn, Honn, skip
            i += 1
        # Now we are at the line that contains '},'
        # Insert new seats
        new_lines.append('          James: \'34H\',\n')
        new_lines.append('          Vicky: \'33H\',\n')
        new_lines.append('          Chenn: \'33K\',\n')
        new_lines.append('          Honn: \'34K\'\n')
        new_lines.append('        },\n')
        # Skip the old closing brace line (the '},')
        i += 1
        continue
    new_lines.append(line)
    i += 1

content = ''.join(new_lines)

# 2. Remove hsr tab from translation objects
# We'll remove the line containing hsr: '...' inside the tabs object for zh and en.
# We'll do a simple line removal, but need to avoid double commas.
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
    # If inside tabs and line starts with hsr:, skip it
    if (in_tabs_zh or in_tabs_en) and stripped.startswith('hsr:'):
        # Skip this line; also we need to possibly remove a trailing comma from previous line if it ends with comma.
        # We'll check the last line in new_lines: if it ends with a comma, we can remove that comma to avoid double comma.
        # However, the hsr line itself ends with a comma (since it's not the last entry). We'll just skip the line.
        # To avoid double commas, we can later clean up.
        continue
    new_lines.append(line)

# Join and clean up double commas
content = '\n'.join(new_lines)
content = re.sub(r',\s*,', ',', content)

# 3. Remove the HSR tab button UI
# Remove the button element with onClick={() => setActiveTab('hsr')}
# We'll use regex to remove the whole button.
content = re.sub(r'<button\s+[^>]*onClick=\{\(\) => setActiveTab\(\'hsr\'\)\}[^>]*>[\s\S]*?</button>', '', content, flags=re.DOTALL)

# 4. Remove the HSR tab heading (likely <h2>🚄 {t.tabs.hsr}</h2>)
content = re.sub(r'<h2[^>]*>\s*🚄\s*\{t\.tabs\.hsr\}\s*</h2>', '', content, flags=re.DOTALL)

# Write back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated index.html')
