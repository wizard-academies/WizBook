"""Each round-4 guard must fail, for the reason it names, when the code it guards is broken. From the repository root:
    uv run --with playwright python docs/arabic-review/round4/mutate.py
"""
import os, subprocess, sys
from pathlib import Path

ROUND1 = Path(__file__).resolve().parent.parent / 'round1'
S = '.claude/skills/wizbook/'
BROWSER = [sys.executable, str(ROUND1 / 'with_chrome.py'), 'engine/check_i18n.py']
TEXT = [sys.executable, '.github/scripts/check_tts_text.py']
RAT_B = r"  t = /^-?\d{1,3}(?:،\d{3})+(?:\.\d+)?$/.test(t) ? t.replace(/،/g, '') : t.replace(/،/g, '.');" + "\n"
FIRST = "  let t = String(str).trim().replace(/[٠-٩۰-۹]/g, d => String(d.charCodeAt(0) & 15));\n"
MERGE = "  if (g[0] === '" + chr(92) + "u200F' && g.length > 1) g.splice(0, 2, g[0] + g[1]);"
MUTANTS = [   # name, file, anchor, replacement, the check, the words its failure must carry
    ('the Arabic comma groups only a bare integer', 'engine/engine.js', r"(?:\.\d+)?$/.test(t)", "$/.test(t)", BROWSER, "rat('١،٠٠٠٫٥') and kin"),
    # round 3's order: the comma decided before the currency sign is taken off
    ('the Arabic comma decided before the currency sign', 'engine/engine.js', FIRST, FIRST + RAT_B, BROWSER, "rat('١،٠٠٠٫٥') and kin"),
    ('stream: the mark is a step of its own', 'engine/engine.js', MERGE, "", BROWSER, 'stream: the first step'),
    ('any digit said ends a number', S + 'scripts/tts.py', "return None if said.endswith(want) else number.group(1)",
     "return None if said else number.group(1)", TEXT, 'from 1914 to 1918'),
    ('the Arabic thousands sign is not part of a number', S + 'scripts/tts.py', r'number = re.search(r"(\d[\d.,٫٬،]*\d|\d)\W*$", clean)',
     r'number = re.search(r"(\d[\d.,]*\d|\d)\W*$", clean)', TEXT, 'الثمن ١٬٠٠٠'),
    ('separators: the Arabic comma is always a point', S + 'scripts/tts.py', 'fixed = fixed.replace("،", "") if', 'fixed = fixed.replace("،", ".") if', TEXT, 'Arabic separators'),
    ('separators: only the thousands sign named', S + 'scripts/tts.py', r'r"\d+(?:[٫٬،]\d+)+"', r'r"\d+(?:[٬]\d+)+"', TEXT, 'Arabic separators'),
]
env = {**os.environ, 'PYTHONIOENCODING': 'utf-8'}
ok = True
for name, rel, a, b, cmd, expect in MUTANTS:
    p = Path(rel)
    orig = p.read_bytes()
    s = orig.decode('utf-8').replace('\r\n', '\n')
    assert s.count(a) == 1, (name, s.count(a))
    p.write_bytes(s.replace(a, b).encode('utf-8'))
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, encoding='utf-8')
    finally:
        p.write_bytes(orig)
    out = r.stdout + r.stderr
    caught = r.returncode != 0 and expect in out
    ok &= caught
    print(f"{'CAUGHT' if caught else 'MISSED'}  {name}" + ('' if caught else f"\n{out[-900:]}"), flush=True)
sys.exit(0 if ok else 1)
