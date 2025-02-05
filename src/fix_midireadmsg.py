import mido
import mido.messages
import mido.midifiles

def fixre_readmsg(infile, status_byte, peek_data, delta, clip=False):
    try: spec = mido.messages.SPEC_BY_STATUS[status_byte]
    except LookupError as le: raise OSError(f"undefined status byte 0x{status_byte:02x}") from le
    data_bytes = peek_data + mido.midifiles.midifiles.read_bytes(infile, spec["length"] - 1 - len(peek_data))
    if clip: data_bytes = [byte if byte < 127 else 127 for byte in data_bytes]
    else:
        for i, byte in enumerate(data_bytes):
            if byte > 127: data_bytes[i] = 127
    return mido.messages.messages.Message.from_bytes([status_byte] + data_bytes, time=delta)
mido.midifiles.midifiles.read_message = fixre_readmsg
