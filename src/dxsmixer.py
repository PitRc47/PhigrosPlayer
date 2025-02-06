from __future__ import annotations

import logging
import typing
import time
from sys import argv

from jnius import autoclass # type: ignore
FFMPEG = autoclass('com.sahib.pyff.ffpy')

import checksys
from tool_funcs import NoJoinThreadFunc

enableKivy = False
if checksys.main == 'Android' or checksys.main == 'Linux':
    logging.info('Change Sound API to Kivy...')
    enableKivy = True
    from kivy.core.audio import SoundLoader
else:
    import dxsound

class musicCls:
    def __init__(self):
        self.dxs = None
        self.buffer = None
        
        self._lflag = 0
        self._volume = 1.0
        
        self._paused = False
        self._pause_pos = 0
        self._pause_volume = 0.0
    
    def _setBufferVolume(self, v: float):
        if self.buffer is None: return
        if enableKivy:
            self.buffer.volume = v
        else:
            self.buffer.SetVolume(self.dxs.transform_volume(v))
     
    def _getBufferPosition(self) -> int:
        if self.buffer is None: return 0
        if enableKivy:
            pass
        else:
            return self.buffer.GetCurrentPosition()[1]
    
    def _setBufferPosition(self, v: int):
        if self.buffer is None: return
        if enableKivy:
            pass
        else:
            minv = 0
            maxv = self.dxs._sdesc.dwBufferBytes - 1
            self.buffer.SetCurrentPosition(min(max(minv, v), maxv))
    
    def _convert(self, fp: str):
        output_file_path = fp + '.wav'
        FFMPEG.Run(f"-i -y {fp} {output_file_path}")
        logging.info(f"File {fp} successfully converted to {output_file_path}")
        return output_file_path
    
    def load(self, fp: str):
        self.unload()
        if enableKivy:
            self.buffer = SoundLoader.load(self._convert(fp))
            if not self.buffer:
                raise RuntimeError("Unable to load sound file!")
        else:
            self.dxs = dxsound.directSound(fp, enable_cache=False)
        
    def unload(self):
        self.dxs = None
        self.buffer = None
        self._paused = False
        
    def play(self, isloop: typing.Literal[0, -1] = 0):
        if not enableKivy:
            self.lflag = 0 if isloop == 0 else 1
            
            if self.buffer is None:
                _, self.buffer = self.dxs.create(self.lflag)
                self._setBufferVolume(self._volume)
            else:
                self.set_pos(0.0)
            
            self.buffer.Play(self.lflag)
        else:
            #self.buffer.loop = isloop
            self.buffer.play()
        
    def stop(self):
        if enableKivy and self.buffer:
            self.buffer.stop()
        self.buffer = None
        
    def pause(self):
        if self._paused: return
        self._paused = True
        
        if enableKivy:
            self.buffer.stop()
        else:
            self._pause_pos = self._getBufferPosition()
            self._pause_volume = self.get_volume()
            self.buffer.Stop()
        
    def unpause(self):
        if not self._paused: return
        self._paused = False
        
        if enableKivy and self.buffer:
            self.buffer.play()
        else:
            self.buffer.Play(self.lflag)
            self._setBufferVolume(self._pause_volume)
            self._setBufferPosition(self._pause_pos)
    
    @NoJoinThreadFunc
    def fadeout(self, t: int):
        if self._paused: return
        
        t /= 1000
        st = time.time()
        bufid = id(self.buffer)
        rvol = self.get_volume()
        
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
        
        self.stop()
        self.set_volume(rvol)
    
    def set_volume(self, volume: float):
        self._volume = volume
        self._setBufferVolume(volume)
        
    def get_volume(self):
        return self._volume
    
    def get_busy(self) -> bool:
        if self.buffer is None:
            return False
        if enableKivy:
            return self.buffer.state
        else:
            return self.buffer.GetStatus() != 0 and not self._paused
    
    def set_pos(self, pos: float):
        if enableKivy:
            self.buffer.seek(pos)
        else:
            self._setBufferPosition(int(pos * self.dxs._sdesc.lpwfxFormat.nAvgBytesPerSec))
        
    def get_pos(self) -> float:
        if enableKivy:
            return self.buffer.get_pos()
        else:
            return self._getBufferPosition() / self.dxs._sdesc.lpwfxFormat.nAvgBytesPerSec
    
    def get_length(self) -> float:
        if enableKivy:
            return self.buffer.length
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