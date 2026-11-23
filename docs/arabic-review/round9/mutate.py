"""From the repository root: python docs/arabic-review/round9/mutate.py docs/arabic-review/round1/with_chrome.py
Each round-9 guard must fail, naming its case, when the code it guards is broken. From the repository root."""
import os, subprocess, sys
from pathlib import Path

BS = chr(92)
CHROME = sys.argv[1]   # with_chrome.py
E = 'engine/engine.js'
MUTANTS = [
    ("an author's right-to-left mark leaves the expression to the browser", E,
     "  const s = String(str ?? '');\n  let out = '', end = 0, ltr = false;",
     "  const s = String(str ?? '');\n  if (s[0] === RLM && !RTL_LETTER.test(s)) return s;\n  let out = '', end = 0, ltr = false;", "u200f5 + x = 7"),
    ("only 'و' may join a number", E, "(?:^|" + BS + "s)[وفبلك]$/", "(?:^|" + BS + "s)و$/", "ف5 + 2 = 7"),
    ("the cover's title is set as typed", E, "$('coverT').textContent = pageText(CHAPTER.title);",
     "$('coverT').textContent = CHAPTER.title;", "cover title"),
]
env = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'BASE_REF': '839a62c'}
ok = True
for name, rel, a, b, expect in MUTANTS:
    p = Path(rel)
    orig = p.read_bytes()
    s = orig.decode('utf-8').replace('\r\n', '\n')
    assert s.count(a) == 1, (name, s.count(a))
    p.write_bytes(s.replace(a, b).encode('utf-8'))
    try:
        r = subprocess.run([sys.executable, CHROME, 'engine/check_i18n.py'], capture_output=True, text=True, env=env, encoding='utf-8')
    finally:
        p.write_bytes(orig)
    out = r.stdout + r.stderr
    caught = r.returncode != 0 and expect in out
    ok &= caught
    print(f"{'CAUGHT' if caught else 'MISSED'}  {name}" + ('' if caught else f"\n{out[-600:]}"), flush=True)
sys.exit(0 if ok else 1)
