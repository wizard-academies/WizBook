"""Each round-1 guard must fail, for the reason it names, when the code it guards is broken. From the repository root:
    uv run --with playwright python docs/arabic-review/round1/mutate.py
"""
import os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = '.claude/skills/wizbook/'
BROWSER = [sys.executable, str(HERE / 'with_chrome.py'), 'engine/check_i18n.py']
TEXT = [sys.executable, '.github/scripts/check_tts_text.py']
MUTANTS = [   # name, file, anchor, replacement, the check, the words its failure must carry
    ('T() sets the bare string', 'engine/engine.js', '  t.textContent = rtlText(str);', '  t.textContent = str;', BROWSER, 'Latin-led Arabic line'),
    ('isRTL ignores the page', 'engine/engine.js', "|| document.documentElement.dir === 'rtl' && RTL_SCRIPT.test(s));\n}\nfunction rtlText", '|| false);\n}\nfunction rtlText', BROWSER, 'Latin-led Arabic line'),
    ('isRTL reads any Arabic letter in an English book', 'engine/engine.js', "|| document.documentElement.dir === 'rtl' && RTL_SCRIPT.test(s));\n}\nfunction rtlText", '|| RTL_SCRIPT.test(s));\n}\nfunction rtlText', BROWSER, 'English stage text changed'),
    ('say() sets a Latin-led line unmarked', S + 'assets/templates/documentary/lib/film.js', "rtlText(ln).split(' ')", "ln.split(' ')", BROWSER, 'say(): Latin-led Arabic line'),
    ('say() shows an Arabic line at once', S + 'assets/templates/documentary/lib/film.js', "mk('tspan', { 'fill-opacity': 0 }, line)", "mk('tspan', {}, line)", BROWSER, 'say(): Arabic line out of order'),
    ('the Arabic comma is not a decimal sign', 'engine/engine.js', ".replace(/[٫،]/g, '.')", ".replace(/٫/g, '.')", BROWSER, "rat('١،٥')"),
    ('cut-short check keeps the punctuation', S + 'scripts/tts.py', 're.findall(word, bare(last_spoken))', '[bare(last_spoken)]', TEXT, 'cut short'),
    ('cut-short check keeps the vowel marks', S + 'scripts/tts.py', 'ends, spoken = re.findall(word, bare(clean[-40:]))', 'ends, spoken = re.findall(word, clean[-40:])', TEXT, 'cut short'),
    ('srt mark by the first letter only', S + 'scripts/export.py', 'or rtl_film and any(map(rtl_letter, line))', '', TEXT, 'srt: Latin-led line in an Arabic film'),
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
