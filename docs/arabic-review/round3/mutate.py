"""Each round-3 guard must fail, for the reason it names, when the code it guards is broken. From the repository root:
    uv run --with playwright python docs/arabic-review/round3/mutate.py
"""
import os, subprocess, sys
from pathlib import Path

ROUND1 = Path(__file__).resolve().parent.parent / 'round1'
S = '.claude/skills/wizbook/'
BROWSER = [sys.executable, str(ROUND1 / 'with_chrome.py'), 'engine/check_i18n.py']
TEXT = [sys.executable, '.github/scripts/check_tts_text.py']
MARK_LINE = r"  if (s[0] === '\u200F' || s[0] === '\u200E') return s[0] === '\u200F';" + "\n  if (!c) return false;\n  if (RTL_LETTER.test(c[0])) return true;\n  if (document"
MUTANTS = [   # name, file, anchor, replacement, the check, the words its failure must carry
    ("the author's mark is ignored", 'engine/engine.js', MARK_LINE, MARK_LINE.split('\n', 1)[1], BROWSER, 'a direction mark ignored'),
    ('the Arabic comma always groups', 'engine/engine.js', "t.replace(/،/g, '') : t.replace(/،/g, '.')", "t.replace(/،/g, '') : t.replace(/،/g, ',')", BROWSER, "rat('"),
    ('the Arabic comma always a decimal point', 'engine/engine.js', r"t = /^[−–-]?\d{1,3}(?:،\d{3})+$/.test(t) ?", "t = false ?", BROWSER, "rat('"),
    ('a text ending in a number: no verdict', S + 'scripts/tts.py', r'return None if re.search(r"\d", last_spoken) else number.group(1)', 'return None', TEXT, "'war'"),
    ('quotes stay on the word', S + 'scripts/tts.py', "ends = [w.strip(\"'-\") for w in", "ends = [w for w in", TEXT, "yes"),
    ('srt: a marked line marked again', S + 'scripts/export.py', r"if not first or line[:1] in ('\u200f', '\u200e'):", "if not first:", TEXT, 'a line the author marked'),
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
