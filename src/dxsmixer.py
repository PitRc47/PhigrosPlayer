from __future__ import annotations

import logging
import typing
import time
from sys import argv

import checksys
from tool_funcs import NoJoinThreadFunc

import dxsound

if checksys.main == 'Android':
    from jnius import autoclass  # type: ignore
    MediaPlayer = autoclass('android.media.MediaPlayer')

class musicCls:
    def __init__(self):
        self.dxs = None
        self.buffer = None
        
        self._lflag = 0
        self._volume = 1.0
        
        self._paused = False
        self._pause_pos = 0
        self._pause_volume = 0.0
        if checksys.main == 'Android':
            self.dxs = MediaPlayer()
    
    def _setBufferVolume(self, v: float):
        if self.buffer is None: return
        if checksys.main == 'Android':
            pass
        else:
            self.buffer.SetVolume(self.dxs.transform_volume(v))
     
    def _getBufferPosition(self) -> int:
        if self.buffer is None: return 0
        if checksys.main == 'Android':
            pass
        else:
            return self.buffer.GetCurrentPosition()[1]
    
    def _setBufferPosition(self, v: int):
        if self.buffer is None: return
        if checksys.main == 'Android':
            pass
        else:
            minv = 0
            maxv = self.dxs._sdesc.dwBufferBytes - 1
            self.buffer.SetCurrentPosition(min(max(minv, v), maxv))
    
    def load(self, fp: str):
        self.unload()
        if checksys.main == 'Android':
            if not self.dxs:
                self.dxs = MediaPlayer()
            self.dxs.setDataSource(fp)
            self.dxs.prepare()
        else:
            self.dxs = dxsound.directSound(fp, enable_cache=False)
        
    def unload(self):
        if checksys.main == 'Android':
            if self.dxs:
                self.dxs.release()
        self.dxs = None
        self.buffer = None
        self._paused = False
        
    def play(self, isloop: typing.Literal[0, -1] = 0):
        self.lflag = False if isloop == 0 else True
        if checksys.main != 'Android':
            
            if self.buffer is None:
                _, self.buffer = self.dxs.create(self.lflag)
                self._setBufferVolume(self._volume)
            else:
                self.set_pos(0.0)
            
            self.buffer.Play(self.lflag)
        else:
            self.dxs.setLooping(self.lflag)
            self.dxs.start()
        
    def stop(self):
        if checksys.main == 'Android':
            if self.dxs:
                self.dxs.stop()
        self.buffer = None
        
    def pause(self):
        if self._paused: return
        self._paused = True
        
        if checksys.main == 'Android':
            if self.dxs:
                self.dxs.pause()
        else:
            self._pause_pos = self._getBufferPosition()
            self._pause_volume = self.get_volume()
            self.buffer.Stop()
        
    def unpause(self):
        if not self._paused: return
        self._paused = False
        
        if checksys.main == 'Android':
            if self.dxs:
                self.dxs.start()
        else:
            self.buffer.Play(self.lflag)
            self._setBufferVolume(self._pause_volume)
            self._setBufferPosition(self._pause_pos)
    
    @NoJoinThreadFunc
    def fadeout(self, t: int):
        if self._paused: return
        t /= 1000.0
        st = time.time()
        if checksys.main != 'Android':
            bufid = id(self.buffer)
        rvol = self.get_volume()
        if checksys.main == 'Android':
            while time.time() - st < t and self.get_busy():
                p = (time.time() - st) / t
                p = max(0.0, min(1.0, p))
                self.set_volume(1.0 - p)
                time.sleep(1 / 15)
        else:
            while (
                time.time() - st < t
                and self.buffer is not None
                and self.get_busy()
            ):
                if id(self.buffer) != bufid:
                    self.set_volume(rvol)
                    return
                    
                p = (time.time() - st) / t
                p = max(0.0, min(1.0, p))
                self.set_volume(1.0 - p)
                time.sleep(1 / 15)
        self.set_volume(rvol)
        self.stop()
    
    def set_volume(self, volume: float):
        self._volume = volume
        if checksys.main == 'Android':
            if self.dxs:
                self.dxs.setVolume(float(volume), float(volume))
        else:
            self._setBufferVolume(volume)
        
    def get_volume(self):
        return self._volume
    
    def get_busy(self) -> bool:
        if checksys.main == 'Android':
            if self.dxs:
                return self.dxs.isPlaying()
            return False
        if self.buffer is None:
            return False
        else:
            return self.buffer.GetStatus() != 0 and not self._paused
    
    def set_pos(self, pos: float):
        if checksys.main == 'Android':
            if self.dxs:
                self.dxs.seekTo(int(pos * 1000))
        else:
            self._setBufferPosition(int(pos * self.dxs._sdesc.lpwfxFormat.nAvgBytesPerSec))
        
    def get_pos(self) -> float:
        if checksys.main == 'Android':
            if self.dxs:
                return self.dxs.getCurrentPosition() / 1000.0
        else:
            return self._getBufferPosition() / self.dxs._sdesc.lpwfxFormat.nAvgBytesPerSec
    
    def get_length(self) -> float:
        if checksys.main == 'Android':
            if self.dxs:
                return self.dxs.getDuration() / 1000.0
        else:
            return self.dxs._sdesc.dwBufferBytes / self.dxs._sdesc.lpwfxFormat.nAvgBytesPerSec
    
class mixerCls:
    def __init__(self):
        self.music = musicCls()
        
    def init(*args, **kwargs) -> None: ...
    
    def Sound(self, fp: str):
        music = musicCls()
        music.load(fp)
        return music

def toDowngradeAPI():
    global mixer
    
    from os import environ; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
    from pygame import mixer as _mixer
    
    _mixer.init(buffer=214748364)
    mixer = _mixer
    
    length = -1
    _load = mixer.music.load
    _get_pos = mixer.music.get_pos
    
    def _loadhook(fn: str):
        nonlocal length
        
        length = _mixer.Sound(fn).get_length()
        _load(fn)
        
    mixer.music.load = _loadhook
    mixer.music.get_length = lambda: length
    mixer.music.get_pos = lambda: _get_pos() / 1000

    
mixer = mixerCls()

if "--soundapi-downgrade" in argv and checksys.main != 'Android':
    toDowngradeAPI()

if __name__ == "__main__":
    mixer.Sound("ShineAfter.ADeanJocularACE.0.ogg")
    mixer.music.play()
    import time
    time.sleep(100)