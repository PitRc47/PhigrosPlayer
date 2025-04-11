import ctypes
import typing
from os.path import isfile

if not all((
    isfile("./libUnityPlugin.so"),
    isfile("./game.dat")
)):
    print("libUnityPlugin.so or game.dat not found in current directory.")
    raise SystemExit

class MemReader:
    def __init__(self, baseAddr: int):
        self.baseAddr = baseAddr
    
    def read(self, offset: int, size: int):
        return ctypes.string_at(self.baseAddr + offset, size)
    
    def getInt(self, offset: int):
        return int.from_bytes(self.read(offset, 4), "little")

so = ctypes.CDLL("./libUnityPlugin.so")
getGlobalMetadata: typing.Callable[[bytes], int] = so._Z26il2cpp_get_global_metadataPKc
getGlobalMetadata.argtypes = (ctypes.c_char_p, )
getGlobalMetadata.restype = ctypes.c_void_p
ggmresult_addr: int = getGlobalMetadata(b"./game.dat")

reader = MemReader(ggmresult_addr)

offset = reader.getInt(8)
size = reader.getInt(offset - 8) + reader.getInt(offset - 4)

metadata = bytearray(reader.read(0, size))
stringSize = reader.getInt(28)
string = reader.getInt(24)

offset = 0
while offset < stringSize:
    xor = offset % 0xFF
    
    i = 0
    while i == 0 or xor != 0:
        xor ^= metadata[string + offset]
        metadata[string + offset] = xor
        offset += 1
        i = 1
    
with open("./global-metadata.dat", "wb") as f:
    f.write(metadata)

print("dumped global-metadata.dat.")
