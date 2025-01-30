from __future__ import annotations

import init_logging as _

import math
import typing
import struct
import logging
import tempfile
import os
from io import BytesIO

import checksys

if checksys.main == 'Android':
    from jnius import autoclass  # type: ignore
    from jnius import cast  # type: ignore
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    MediaPlayer = autoclass('android.media.MediaPlayer')
    File = autoclass('java.io.File')
    FileInputStream = autoclass('java.io.FileInputStream')
    FileDescriptor = autoclass('java.io.FileDescriptor')
else:
    import win32comext.directsound.directsound as ds
    import win32event as w32e
    from pywintypes import WAVEFORMATEX
    from pydub import AudioSegment

CACHE_BUFFER_MAXSIZE = 32
PRE_CACHE_SIZE = CACHE_BUFFER_MAXSIZE
RING_BUFFER = True

_WAV_HEADER = "<4sl4s4slhhllhh4sl"
_WAV_HEADER_LENGTH = struct.calcsize(_WAV_HEADER)

if checksys.main == 'Windows':
    dxs = ds.DirectSoundCreate(None, None)
    dxs.SetCooperativeLevel(None, ds.DSSCL_NORMAL)

# region Windows Audio Processing
if checksys.main == 'Windows':
    def _wav2wfx(data: bytes):
        (
            format,
            nchannels,
            samplespersecond,
            datarate,
            blockalign,
            bitspersample,
            data
        ) = struct.unpack(_WAV_HEADER, data)[5:-1]
        wfx = WAVEFORMATEX()
        wfx.wFormatTag = format
        wfx.nChannels = nchannels
        wfx.nSamplesPerSec = samplespersecond
        wfx.nAvgBytesPerSec = datarate
        wfx.nBlockAlign = blockalign
        wfx.wBitsPerSample = bitspersample
        return wfx

    def _seg2wfx(seg: AudioSegment):
        wfx = WAVEFORMATEX()
        wfx.wFormatTag = 1
        wfx.nChannels = seg.channels
        wfx.nSamplesPerSec = seg.frame_rate
        wfx.nAvgBytesPerSec = seg.frame_rate * seg.channels * seg.sample_width
        wfx.nBlockAlign = seg.channels * seg.sample_width
        wfx.wBitsPerSample = seg.sample_width * 8
        return wfx

    def _loadDirectSound(data: bytes):
        sdesc = ds.DSBUFFERDESC()
        
        seg: AudioSegment = AudioSegment.from_file(BytesIO(data))
        bufdata = seg.raw_data
        sdesc.lpwfxFormat = _seg2wfx(seg)
        
        if len(bufdata) > ds.DSBSIZE_MAX:
            logging.warning(f"Sound buffer size is too large ({len(bufdata)} > {ds.DSBSIZE_MAX}), truncated.")
            bufdata = bufdata[:ds.DSBSIZE_MAX]
            
        sdesc.dwBufferBytes = len(bufdata)
        
        return bufdata, sdesc
# endregion

class directSoundAndroid:
    def __init__(self, data: bytes | str, enable_cache: bool = True):
        if isinstance(data, str):
            # 直接使用文件路径
            self._file_path = data
        else:
            # 将字节数据写入临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(data)
                self._file_path = f.name
        
        self._enable_cache = enable_cache
        self._volume = 1.0  # 0.0 to 1.0
        self._media_player = MediaPlayer()
        
        try:
            # 创建文件输入流并获取文件描述符
            fis = FileInputStream(self._file_path)
            fd = cast('java.io.FileDescriptor', fis.getFD())
            self._media_player.setDataSource(fd)
            self._media_player.prepare()
        finally:
            fis.close()
            if not isinstance(data, str):
                os.remove(self._file_path)
    
    def set_volume(self, v: float):
        self._volume = max(0.0, min(1.0, v))
        self._media_player.setVolume(self._volume, self._volume)
    
    def play(self, wait: bool = False):
        self._media_player.start()
        if wait:
            while self._media_player.isPlaying():
                pass
        return self._media_player
    
    def stop(self):
        self._media_player.stop()
        self._media_player.prepare()
    
    def release(self):
        self._media_player.release()

class directSound:
    def __new__(cls, data: bytes | str, enable_cache: bool = True):
        if checksys.main == 'Android':
            return directSoundAndroid(data, enable_cache)
        else:
            instance = super().__new__(cls)
            instance.__init__(data, enable_cache)
            return instance
    
    def __init__(self, data: bytes | str, enable_cache: bool = True):
        if isinstance(data, str): 
            with open(data, "rb") as f:
                data = f.read()
        
        self._bufdata, self._sdesc = _loadDirectSound(data)
        self._sdesc.dwFlags = ds.DSBCAPS_CTRLVOLUME | ds.DSBCAPS_CTRLPOSITIONNOTIFY | ds.DSBCAPS_GLOBALFOCUS | ds.DSBCAPS_GETCURRENTPOSITION2
        
        self._enable_cache = enable_cache
        self._volume = 0  # -10000 ~ 0
        self._buffers = []
        
        if self._enable_cache:
            self._buffers.extend(self._create() for _ in range(PRE_CACHE_SIZE))
    
    def _create(self):
        event = w32e.CreateEvent(None, 0, 0, None)
        buffer = dxs.CreateSoundBuffer(self._sdesc, None)
        buffer.QueryInterface(ds.IID_IDirectSoundNotify).SetNotificationPositions((-1, event))
        buffer.Update(0, self._bufdata)
        buffer.SetVolume(self._volume)
        return event, buffer
    
    def create(self, playMethod: typing.Literal[0, 1]):
        if self._enable_cache:
            if len(self._buffers) > CACHE_BUFFER_MAXSIZE:
                for i in reversed(self._buffers):
                    e, buf = i
                    if buf.GetStatus() == 0:
                        try: self._buffers.remove(i)
                        except ValueError: continue
                        break
            
            if self._buffers:
                for e, buf in self._buffers:
                    if buf.GetStatus() == 0:
                        buf.SetVolume(self._volume)
                        buf.SetCurrentPosition(0)
                        buf.Play(playMethod)
                        return e, buf
                
                if RING_BUFFER:
                    e, buf = self._buffers[0]
                    buf.Stop()
                    buf.SetVolume(self._volume)
                    buf.SetCurrentPosition(0)
                    buf.Play(playMethod)
                    return e, buf
        
        event, buffer = self._create()
        buffer.Play(playMethod)
        if self._enable_cache:
            self._buffers.append((event, buffer))
        return event, buffer
    
    def transform_volume(self, v: float):
        if v <= 1e-5: return ds.DSBVOLUME_MIN
        if v >= 1.0: return ds.DSBVOLUME_MAX
        return int(2000 * math.log10(v))
    
    def set_volume(self, v: float):
        self._volume = self.transform_volume(v)
    
    def play(self, wait: bool = False, playMethod: typing.Literal[0, 1] = 0):
        event, buffer = self.create(playMethod)
        
        if wait:
            w32e.WaitForSingleObject(event, -1)
        
        return event, buffer
    
    def stop(self):
        pass  # Windows版本停止逻辑已在buffer.Stop()处理
    
    def release(self):
        pass  # Windows版本资源释放由系统管理