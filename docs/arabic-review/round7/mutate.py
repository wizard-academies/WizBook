"""Each round-7 guard must fail, for the reason it names, when the code it guards is broken. From the repository root:
    uv run --with playwright python docs/arabic-review/round7/mutate.py
"""
import os, subprocess, sys
from pathlib import Path

ROUND1 = Path(__file__).resolve().parent.parent / 'round1'
BROWSER = [sys.executable, str(ROUND1 / 'with_chrome.py'), 'engine/check_i18n.py']
SKILL = [sys.executable, '.github/scripts/check_skill.py']
MUTANTS = [   # name, file, anchor, replacement, the check, the words its failure must carry
    ("English identity: a base from before the rename is not found", 'engine/check_i18n.py',
     'relative.replace(".claude/skills/wizbook/", ".claude/skills/papermorph/", 1)', 'relative', BROWSER,
     'the book template is not at BASE_REF'),
    ("the review record's links are checked", 'docs/arabic-review/README.md',
     '[٦](round6/ADJUDICATION.md)', '[٦](round9/ADJUDICATION.md)', SKILL, 'round9/ADJUDICATION.md'),
    ("the Arabic front page's links are checked", 'README.ar.md',
     '(docs/arabic-review/)', '(docs/arabic-reviews/)', SKILL, 'docs/arabic-reviews/'),
]
env = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'BASE_REF': os.environ.get('BASE_REF', '839a62c')}
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
