"""Each round-2 guard must fail, for the reason it names, when the code it guards is broken. From the repository root:
    uv run --with playwright python docs/arabic-review/round2/mutate.py
"""
import os, subprocess, sys
from pathlib import Path

ROUND1 = Path(__file__).resolve().parent.parent / 'round1'
S = '.claude/skills/wizbook/'
BROWSER = [sys.executable, str(ROUND1 / 'with_chrome.py'), 'engine/check_i18n.py']
TEXT = [sys.executable, '.github/scripts/check_tts_text.py']
MUTANTS = [   # name, file, anchor, replacement, the check, the words its failure must carry
    ('any Arabic letter makes a line Arabic', 'engine/engine.js', 'return rtl > 0 && 2 * rtl >= words.length;', 'return rtl > 0;', BROWSER, 'Latin-led line misread'),
    ('a marked string is marked again', 'engine/engine.js', "return s[0] !== '\\u200F' && isRTL(s)", 'return isRTL(s)', BROWSER, 'marked twice'),
    ('the Arabic comma is a decimal point again', 'engine/engine.js', ".replace(/،/g, ',')", ".replace(/،/g, '.')", BROWSER, "rat('١،٠٠٠')"),
    ('cut at a number: silent', S + 'scripts/tts.py', 'return ends[-1] if re.search(r"\\d", last_spoken) else None', 'return None', TEXT, '1914'),
    ('a word said in parts warns', S + 'scripts/tts.py', ' or end.endswith("-" + said)', '', TEXT, 'twenty-one'),
    ('case decides', S + 'scripts/tts.py', 'end, said = ends[-1].lower(), spoken[-1].lower()', 'end, said = ends[-1], spoken[-1]', TEXT, 'NATO'),
    ('srt: any Arabic letter marks the line', S + 'scripts/export.py', 'rtl_film and rtl and 2 * rtl >= len(words)', 'rtl_film and rtl', TEXT, 'quoting one Arabic word'),
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
