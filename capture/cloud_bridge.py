"""Linux cloud-game capture boundary. No daily/combat automation is enabled.

Design references: ok-ww's browser device boundary and March7thAssistant's
video-frame capture. Kept standalone because ok-script still imports Win32.
"""
from __future__ import annotations
import base64
import math
import time
from dataclasses import dataclass


class NotReady(RuntimeError):
    pass


@dataclass(frozen=True)
class Geometry:
    x: float
    y: float
    width: float
    height: float
    native_width: int
    native_height: int
    object_fit: str = 'contain'

    def point(self, x: float, y: float) -> tuple[float, float]:
        if not all(math.isfinite(v) for v in (x, y, self.x, self.y, self.width, self.height)):
            raise NotReady('invalid geometry')
        if min(self.width, self.height, self.native_width, self.native_height) <= 0:
            raise NotReady('empty game surface')
        if not (0 <= x < self.native_width and 0 <= y < self.native_height):
            raise NotReady('input outside game frame')
        if self.object_fit == 'fill':
            sx, sy = self.width/self.native_width, self.height/self.native_height
        elif self.object_fit == 'contain':
            sx = sy = min(self.width/self.native_width, self.height/self.native_height)
        else:
            raise NotReady('unsupported video object-fit; input blocked')
        left = self.x+(self.width-self.native_width*sx)/2
        top = self.y+(self.height-self.native_height*sy)/2
        return left+x*sx, top+y*sy


class CloudBridge:
    def __init__(self, page, *, allow_input=False):
        self.page = page
        self.allow_input = allow_input
        self.surface = None
        self.last_capture = 0.0
        self.geometry = None
        self.held_keys = set()

    def locate(self):
        # Search frames independently so an iframe offset is included by
        # Playwright's bounding_box (top-level CSS coordinates).
        choices = []
        for frame in self.page.frames:
            for element in frame.locator('video').all():
                if not element.is_visible():
                    continue
                info = element.evaluate('''v => ({width:v.videoWidth,height:v.videoHeight,
                  ready:v.readyState,paused:v.paused,ended:v.ended,time:v.currentTime,
                  fit:getComputedStyle(v).objectFit,position:getComputedStyle(v).objectPosition})''')
                box = element.bounding_box()
                if box and info['ready'] >= 2 and not info['paused'] and not info['ended'] and info['width'] >= 640 and info['height'] >= 360:
                    choices.append((box['width']*box['height'], element, info, box))
        if len(choices) != 1:
            raise NotReady('waiting for a unique playing game video')
        _, self.surface, info, box = choices[0]
        if info['position'] != '50% 50%':
            raise NotReady('non-centered video; input blocked')
        self.geometry = Geometry(box['x'],box['y'],box['width'],box['height'],info['width'],info['height'],info['fit'])
        return info

    def capture(self) -> tuple[bytes, Geometry]:
        self.locate()
        # Copy decoded pixels, not browser chrome; tainted frames fail closed.
        encoded = self.surface.evaluate('''v => {
          const c=document.createElement('canvas');c.width=v.videoWidth;c.height=v.videoHeight;
          c.getContext('2d').drawImage(v,0,0);return c.toDataURL('image/png').split(',')[1];
        }''')
        data = base64.b64decode(encoded, validate=True)
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            raise NotReady('invalid screenshot')
        self.last_capture = time.monotonic()
        return data, self.geometry

    def click(self, x, y):
        if not self.allow_input:
            raise NotReady('input is disabled for this probe')
        if time.monotonic()-self.last_capture > 1:
            raise NotReady('stale frame; input blocked')
        old_geometry = self.geometry
        self.locate()
        if self.geometry != old_geometry:
            raise NotReady('video moved since capture; recapture required')
        self.page.mouse.click(*self.geometry.point(x,y))

    def release(self):
        for key in list(self.held_keys):
            try:
                self.page.keyboard.up(key)
            finally:
                self.held_keys.discard(key)
