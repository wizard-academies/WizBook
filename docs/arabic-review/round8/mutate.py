"""Each round-8 guard must fail, for the reason it names, when the code it guards is broken. From the repository root:
    uv run --with playwright python docs/arabic-review/round8/mutate.py
"""
import os, subprocess, sys
from pathlib import Path

ROUND1 = Path(__file__).resolve().parent.parent / 'round1'
BROWSER = [sys.executable, str(ROUND1 / 'with_chrome.py'), 'engine/check_i18n.py']
E = 'engine/engine.js'
BS = chr(92)   # a backslash: the invisible characters are named by their codes
FILM = '.claude/skills/wizbook/assets/templates/documentary/lib/film.js'
MUTANTS = [   # name, file, anchor, replacement, the words the check's failure must carry
    ("a card's text is set as typed", E, "s.append(typeof p === 'string' ? pageText(p) :", "s.append(typeof p === 'string' ? p :", 'card: an expression is out of order'),
    ("the stage's text is set as typed", E, "const m = pageText(s), out =", "const m = s, out =", 'stage: the expression is out of order'),
    ("a caption is set as typed", E, "$('caption').textContent = pageText(text);", "$('caption').textContent = text;", 'caption:'),
    ("a question's kicker is set as typed", E, "h('p', 'kicker', pageText(kick))", "h('p', 'kicker', kick)", 'card texts outside rich()'),
    ("a table's column buttons are set as typed", E, "typeof lab === 'string' ? pageText(lab) : lab", "lab", 'card texts outside rich()'),
    ("the finish card's title is set as typed", E, "h('p', 'prompt', pageText(CHAPTER.title))", "h('p', 'prompt', CHAPTER.title)", 'card texts outside rich()'),
    ("an English page is isolated too", E, "const pageText = str => document.documentElement.dir === 'rtl' ? ltrMaths(str) : str;",
     "const pageText = str => ltrMaths(str);", 'English text changed'),
    ("a range of years is taken for a subtraction", E, "const EXPRESSION_SIGN = /[=+×÷*<>≤≥≠^−]/", r"const EXPRESSION_SIGN = /[=+×÷*<>≤≥≠^−\-]/", '1914 - 1918'),
    ("a sum in Arabic-Indic digits is isolated", E, "!EXPRESSION_SIGN.test(e) || !EXPRESSION_LTR.test(e) || ltr", "!EXPRESSION_SIGN.test(e) || ltr", 'و ٥ + ٢ = ٧ صح'),
    ("an expression after Latin words is isolated", E, "!EXPRESSION_SIGN.test(e) || !EXPRESSION_LTR.test(e) || ltr", "!EXPRESSION_SIGN.test(e) || !EXPRESSION_LTR.test(e)",
     'The answer: 5 + 2 = 7.'),
    ("a one-letter Arabic name across a sign does not hold", E, r"LTR_WORD.test(m[1].slice(-1)) || /^\p{Script=Arabic}\p{M}*$/u.test(m[1]);",
     "LTR_WORD.test(m[1].slice(-1));", 'س + 3 = 7'),
    ("an Arabic word across a sign holds", E, r"LTR_WORD.test(m[1].slice(-1)) || /^\p{Script=Arabic}\p{M}*$/u.test(m[1]);",
     r"LTR_WORD.test(m[1].slice(-1)) || /\p{Script=Arabic}/u.test(m[1]);", 'الناتج = 7 + 2'),
    ("a list item's sign holds", E, "return m[1] === '' ? m.index !== 0 :", "return m[1] === '' ? true :", '- x = 5'),
    ("'and' joined to a number holds", E, r" && !/(?:^|\s)و$/.test(before))", ")", 'و5 + 2 = 7'),
    ("an expression joined to a word (an Arabic word, a web address) is isolated", E, r'''(p && p !== RLM && p !== LRM && !/[\s(\[«"'“‘،:؛]/.test(p) && !/(?:^|\s)و$/.test(before))''', "false",
     'قيمةx = 5'),
    ("a time is taken for a sum", E, "|| (/[،:؛]/.test(p) && LTR_WORD.test(before.slice(-2, -1)))", "", 'الوقت 10:5 + 3'),
    ("a number's unit is left out", E, r"(?:${number}(?:[^\S\n]?${name})?[%٪°]?", r"(?:${number}(?:${name})?[%٪°]?", 'المسافة 5 km'),
    ("a line its author marked right to left is isolated", E,
     "  if (s[0] === RLM && !RTL_LETTER.test(s)) return s;", "", "ltrMaths('" + BS + "u200f5 + 2 = 7')"),
    ("a bracket is parted from its partner", E, r"for (let k = opens - closes; k > 0 && /[(\[]/.test(e[a]); k--) a++;", "", 'x = 5 مثلا'),
    ("stream: an isolate's close is a step of its own", E, "else if (c === PDI && g.length && !lead) g[g.length - 1] += c;", "", 'stream: a step shows nothing new'),
    ("stream: an isolate's opening is a step of its own", E, "if (c === RLM || c === LRM || c === LRI) lead += c;", "if (c === RLM || c === LRM) lead += c;",
     'stream: a step shows nothing new'),
    ("stream: a mark at the end is a step of its own", E, "if (lead) { if (g.length) g[g.length - 1] += lead; else g.push(lead); }", "if (lead) g.push(lead);",
     'stream: a step shows nothing new'),
    ("say(): an isolated expression is split into words", FILM, "ws.length && /" + BS + "u2066[^" + BS + "u2069]*$/.test(ws.at(-1))", "false", 'say():'),
]
env = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'BASE_REF': os.environ.get('BASE_REF', '839a62c')}
ok = True
for name, rel, a, b, expect in MUTANTS:
    p = Path(rel)
    orig = p.read_bytes()
    s = orig.decode('utf-8').replace('\r\n', '\n')
    assert s.count(a) == 1, (name, s.count(a))
    p.write_bytes(s.replace(a, b).encode('utf-8'))
    try:
        r = subprocess.run(BROWSER, capture_output=True, text=True, env=env, encoding='utf-8')
    finally:
        p.write_bytes(orig)
    out = r.stdout + r.stderr
    caught = r.returncode != 0 and expect in out
    ok &= caught
    print(f"{'CAUGHT' if caught else 'MISSED'}  {name}" + ('' if caught else f"\n{out[-700:]}"), flush=True)
sys.exit(0 if ok else 1)
