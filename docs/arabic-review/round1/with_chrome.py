"""Run a Playwright check script on the installed Google Chrome instead of Playwright's own Chromium download,
or on that download when Chrome is not installed.
    uv run --with playwright python with_chrome.py engine/check_i18n.py [args...]
"""
import runpy, sys
from playwright._impl.browser_type import BrowserType

_launch = BrowserType.launch


async def launch(self, *args, **kwargs):
    if self.name == 'chromium' and not kwargs.get('executablePath') and not kwargs.get('channel'):
        try:
            return await _launch(self, *args, **{**kwargs, 'channel': 'chrome'})
        except Exception as e:
            print(f'with_chrome: no Google Chrome ({str(e).splitlines()[0]}), using the Chromium Playwright installed', file=sys.stderr)
    return await _launch(self, *args, **kwargs)

BrowserType.launch = launch
script = sys.argv[1]
sys.argv = sys.argv[1:]
runpy.run_path(script, run_name='__main__')
