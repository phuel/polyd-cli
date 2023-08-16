class PolyD_Cmd:
    SET_DEVICE_ID  = 0x00
    RESERVED       = 0x02
    GET_FW_VERSION = 0x08
    SET_MIDI_CHANNELS = 0x0E
    SET_MIDI_IN_TRANSPOSE = 0x0F
    SET_VELOCITY_INFO = 0x10
    SET_PITCH_BEND_RANGE = 0x11
    SET_KEY_PRIORITY = 0x12
    SET_MULTI_TRIGGER = 0x14
    SET_MOD_CURVE = 0x15
    SET_NOTE_AT_ZERO = 0x16
    SET_CLOCK_OUT = 0x17
    SET_EXT_CLOCK_POLARITY = 0x19
    SET_SYNC_RATE = 0x1A
    SET_CLOCK_SOURCE = 0x1B
    SET_ACCENT_VELOCITY = 0x1C
    SET_MOD_WHEEL_RANGE = 0x20
    SET_MOD_WHEEL_OUT = 0x21
    SET_PITCH_BEND_OUT = 0x22
    SET_KEY_OUT = 0x23
    SET_AFTER_TOUCH_OUT = 0x24
    SET_SEQ_OUT = 0x25
    SET_ARP_OUT = 0x26
    SET_LOCAL_MODE = 0x2F
    GET_SETTINGS = 0x75
    SET_SEQ_PATTERN = 0x77
    RESTORE_FACTORY_SETTINGS = 0x7D

    @staticmethod
    def make_sysex(did, data):
        sysex_start = bytes([0xF0, 0x00, 0x20, 0x32, 0x00, 0x01, 0x0c])
        sysex = bytearray(sysex_start)
        sysex.append(did)
        sysex.extend(data)
        sysex.append(0xF7)
        return sysex
