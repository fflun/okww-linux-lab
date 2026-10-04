"""Manual login / capture probe; never clicks Start or starts a daily task."""
import json
import os
import signal
import time
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from cloud_bridge import CloudBridge, NotReady

ROOT=Path(os.environ.get('OKWW_CAPTURE_DIR', str(Path.home()/'.local/share/okww-linux-lab')))
URL='https://mc.kurogames.com/cloud/index.html'
stop=False
def halt(*_):
    global stop
    stop=True
signal.signal(signal.SIGTERM,halt)
signal.signal(signal.SIGINT,halt)

def main():
    os.umask(0o077)
    ROOT.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        context=p.chromium.launch_persistent_context(
            str(ROOT/'profile'), executable_path='/usr/bin/chromium',
            headless=False, chromium_sandbox=True,
            viewport={'width':1280,'height':720},device_scale_factor=1,
            args=['--disable-dev-shm-usage','--no-first-run','--lang=zh-CN',
                  '--disable-background-timer-throttling','--disable-renderer-backgrounding'])
        page=context.pages[0] if context.pages else context.new_page()
        failures=[]
        def failed(request):
            failures.append({'host':urlsplit(request.url).hostname,'reason':request.failure})
        def response(r):
            if r.status>=400:
                failures.append({'host':urlsplit(r.url).hostname,'status':r.status})
        page.on('requestfailed',failed)
        page.on('response',response)
        try:
            page.goto(URL,wait_until='domcontentloaded',timeout=45000)
        except Exception as exc:
            print('Page navigation delayed:',type(exc).__name__,flush=True)
        bridge=CloudBridge(page)
        try:
            while not stop:
                state={'checked_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                       'automation_enabled':False,'input_enabled':False}
                try:
                    data,geometry=bridge.capture()
                    state.update(state='VIDEO_CAPTURE_CANDIDATE',native_size=[geometry.native_width,geometry.native_height],game_scene_verified=False)
                    # Only the latest frame, never history or account details in logs.
                    (ROOT/'last-frame.png').write_bytes(data)
                except NotReady as exc:
                    state.update(state='WAITING_FOR_GAME',reason=str(exc))
                except Exception as exc:
                    state.update(state='CAPTURE_UNVERIFIED',reason=type(exc).__name__)
                (ROOT/'status.json').write_text(json.dumps(state,ensure_ascii=False),encoding='utf-8')
                (ROOT/'network.json').write_text(json.dumps(failures[-30:]),encoding='utf-8')
                page.wait_for_timeout(5000)
        finally:
            bridge.release()
            context.close()

if __name__=='__main__':
    main()
