"""Each round-5 guard must fail, for the reason it names, when the code it guards is broken. From the repository root:
    uv run --with playwright python docs/arabic-review/round5/mutate.py
"""
import os, subprocess, sys
from pathlib import Path

ROUND1 = Path(__file__).resolve().parent.parent / 'round1'
S = '.claude/skills/wizbook/'
BROWSER = [sys.executable, str(ROUND1 / 'with_chrome.py'), 'engine/check_i18n.py']
TEXT = [sys.executable, '.github/scripts/check_tts_text.py']
LRM = " || g[0] === '" + chr(92) + "u200E'"
MUTANTS = [   # name, file, anchor, replacement, the check, the words its failure must carry
    ("the voice's digits only need to end the same", S + 'scripts/tts.py',
     'return None if said and digits(said[-1]) == digits(number.group(1)) else number.group(1)',
     'return None if digits(last_spoken).endswith(digits(number.group(1))) else number.group(1)', TEXT, 'fell from 15 to 5'),
    ('separators: any two numbers get a suggestion', S + 'scripts/tts.py', r'elif re.fullmatch(r"\d+[٫،]\d+", n):', 'elif True:', TEXT, 'no one number'),
    ('separators: thousands signs may differ', S + 'scripts/tts.py', r'(?:\1\d{3})*(?:٫\d+)?', r'(?:[٬،]\d{3})*(?:٫\d+)?', TEXT, 'no one number'),
    ('stream: the left-to-right mark is a step of its own', 'engine/engine.js', LRM, '', BROWSER, 'stream: the first step'),
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
