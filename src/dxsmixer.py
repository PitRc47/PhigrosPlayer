from __future__ import annotations

import typing
import time
from sys import argv

import checksys
import dxsound
import tool_funcs

if checksys.main == 'Android':
    from jnius import autoclass, cast  # type: ignore
    FileInputStream = autoclass('java.io.FileInputStream')

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
        if checksys.main == 'Android':
            self.dxs.set_volume(v)
        else:
            self.buffer.SetVolume(self.dxs.transform_volume(v))
     
    def _getBufferPosition(self) -> int:
        if self.buffer is None: return 0
        if checksys.main == 'Android':
            # 返回当前播放位置（毫秒转换为字节位置）
            current_time_ms = self.dxs._media_player.getCurrentPosition()
            byte_position = int(current_time_ms / 1000 * 
                               self.dxs._media_player.getSampleRate() *
                               self.dxs._media_player.getAudioChannels() *
                               self.dxs._media_player.getAudioFormat() // 8)
            return byte_position
        else:
            return self.buffer.GetCurrentPosition()[1]
    
    def _setBufferPosition(self, v: int):
        if self.buffer is None: return
        if checksys.main == 'Android':
            # Android使用时间（秒）定位，需将字节位置转换为时间
            pos_seconds = v / (self.dxs._media_player.getSampleRate() * 
                              self.dxs._media_player.getAudioChannels() *
                              self.dxs._media_player.getAudioFormat() // 8)
            self.dxs._media_player.seekTo(int(pos_seconds * 1000))
        else:
            minv = 0
            maxv = self.dxs._sdesc.dwBufferBytes - 1
            self.buffer.SetCurrentPosition(min(max(minv, v), maxv))
    
    def load(self, fp: str):
        self.unload()
        self.dxs = dxsound.directSound(fp, enable_cache=False)
        
    def unload(self):
        self.dxs = None
        self.buffer = None
        self._paused = False
        
    def play(self, isloop: typing.Literal[0, -1] = 0):
        self.lflag = 0 if isloop == 0 else 1
        
        if self.buffer is None:
            _, self.buffer = self.dxs.create(self.lflag)
            self._setBufferVolume(self._volume)
        else:
            if checksys.main == 'Android':
                self.buffer.reset()
                fis = FileInputStream(self.dxs._file_path)
                fd = cast('java.io.FileDescriptor', fis.getFD())
                self.buffer.setDataSource(fd)
                self.buffer.prepare()
                fis.close()
            self.set_pos(0.0)
        
        # 开始播放
        if checksys.main == 'Android':
            if not self.buffer.isPlaying():
                self.buffer.start()
        else:
            self.buffer.Play(self.lflag)
        
    def stop(self):
        if checksys.main == 'Android' and self.buffer is not None:
            self.buffer.release()
            self.buffer = None
        else:
            self.buffer = None
        
    def pause(self):
        if self._paused: return
        self._paused = True
        
        if checksys.main == 'Android':
            self.dxs._media_player.pause()
        else:
            self._pause_pos = self._getBufferPosition()
            self._pause_volume = self.get_volume()
            self.buffer.Stop()
        
    def unpause(self):
        if not self._paused: return
        self._paused = False
        
        if checksys.main == 'Android':
            self.dxs._media_player.start()
        else:
            self.buffer.Play(self.lflag)
            self._setBufferVolume(self._pause_volume)
            self._setBufferPosition(self._pause_pos)
    
    @tool_funcs.NoJoinThreadFunc
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
        if checksys.main == 'Android':
            return self.dxs._media_player.isPlaying() and not self._paused
        else:
            return self.buffer.GetStatus() != 0 and not self._paused
    
    def set_pos(self, pos: float):
        if checksys.main == 'Android':
            self.dxs._media_player.seekTo(int(pos * 1000))
        else:
            self._setBufferPosition(int(pos * self.dxs._sdesc.lpwfxFormat.nAvgBytesPerSec))
        
    def get_pos(self) -> float:
        if checksys.main == 'Android':
            return self.dxs._media_player.getCurrentPosition() / 1000.0
        else:
            return self._getBufferPosition() / self.dxs._sdesc.lpwfxFormat.nAvgBytesPerSec
    
    def get_length(self) -> float:
        if checksys.main == 'Android':
            return self.dxs._media_player.getDuration() / 1000.0  # 毫秒转秒
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
    
    if checksys.main != 'Android':
        from os import environ; environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
        from pygame import mixer as _mixer
        _mixer.Sound
        
        _mixer.init()
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

if "--soundapi-downgrade" in argv:
    toDowngradeAPI()
    