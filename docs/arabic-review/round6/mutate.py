"""Each round-6 guard must fail, for the reason it names, when the code it guards is broken. From the repository root:
    uv run --with playwright python docs/arabic-review/round6/mutate.py
"""
import os, subprocess, sys
from pathlib import Path

ROUND1 = Path(__file__).resolve().parent.parent / 'round1'
S = '.claude/skills/wizbook/'
BROWSER = [sys.executable, str(ROUND1 / 'with_chrome.py'), 'engine/check_i18n.py']
TEXT = [sys.executable, '.github/scripts/check_tts_text.py']
MUTANTS = [   # name, file, anchor, replacement, the check, the words its failure must carry
    ('the thousands-sign-then-comma branch removed', S + 'scripts/tts.py',
     r'''        elif re.fullmatch(r"\d{1,3}(?:٬\d{3})+،(?!\d{3}$)\d+", n):   # ٬ groups, then ، before the decimal part
            fixed = n.replace("٬", "").replace("،", ".")
''', '', TEXT, 'no one number'),
    ('a comma before three digits read as a decimal', S + 'scripts/tts.py', r'،(?!\d{3}$)\d+', r'،\d+', TEXT, 'no one number'),
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
