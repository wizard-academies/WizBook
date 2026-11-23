"""Run a Playwright check script on the installed Google Chrome instead of Playwright's own Chromium download.
    uv run --with playwright python with_chrome.py engine/check_i18n.py [args...]
"""
import runpy, sys
from playwright._impl.browser_type import BrowserType

_launch = BrowserType.launch


async def launch(self, *args, **kwargs):
    if self.name == 'chromium' and not kwargs.get('executablePath') and not kwargs.get('channel'):
        kwargs['channel'] = 'chrome'
    return await _launch(self, *args, **kwargs)

BrowserType.launch = launch
script = sys.argv[1]
sys.argv = sys.argv[1:]
runpy.run_path(script, run_name='__main__')
