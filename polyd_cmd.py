class PolyD_Cmd:
    SET_DEVICE_ID            = 0x00
    RESULT                   = 0x01
    RESERVED                 = 0x02
    RESERVED_RESULT          = 0x03
    GET_FW_VERSION           = 0x08
    FW_VERSION_RESULT        = 0x09
    SET_MIDI_CHANNELS        = 0x0E
    SET_MIDI_IN_TRANSPOSE    = 0x0F
    SET_VELOCITY_INFO        = 0x10
    SET_PITCH_BEND_RANGE     = 0x11
    SET_KEY_PRIORITY         = 0x12
    SET_MULTI_TRIGGER        = 0x14
    SET_MOD_CURVE            = 0x15
    SET_NOTE_AT_ZERO         = 0x16
    SET_CLOCK_OUT            = 0x17
    SET_EXT_CLOCK_POLARITY   = 0x19
    SET_SYNC_RATE            = 0x1A
    SET_CLOCK_SOURCE         = 0x1B
    SET_ACCENT_VELOCITY      = 0x1C
    SET_MOD_WHEEL_RANGE      = 0x20
    SET_MOD_WHEEL_OUT        = 0x21
    SET_PITCH_BEND_OUT       = 0x22
    SET_KEY_OUT              = 0x23
    SET_AFTER_TOUCH_OUT      = 0x24
    SET_SEQ_OUT              = 0x25
    SET_ARP_OUT              = 0x26
    SET_LOCAL_MODE           = 0x2F
    GET_SETTINGS             = 0x75
    SETTINGS_RESULT          = 0x76
    GET_SEQ_PATTERN          = 0x77
    SEQ_PATTERN              = 0x78
    RESTORE_FACTORY_SETTINGS = 0x7D

    SEQ_PREFIX = (0x23, 0x98, 0x54, 0x76, 0x00, 0x00, 0x00, 0x0C,
                  0x00, 0x50, 0x00, 0x4F, 0x00, 0x4C, 0x00, 0x59,
                  0x00, 0x20, 0x00, 0x44, 0x00, 0x00, 0x00, 0x0A,
                  0x00, 0x31, 0x00, 0x2E, 0x00, 0x31, 0x00, 0x2E,
                  0x00, 0x33, 0x00, 0x00, 0x01, 0x75 )

    SYX_PREFIX = (0xF0,              # Sysex start
                  0x00, 0x20, 0x32,  # Manufacturer Id
                  0x00, 0x01, 0x0c)  # Model Id
    
    SEQ_SIZE = 411
    PATTERN_SYX_SIZE = 389
    PATTERN_SIZE = 373

    @staticmethod
    def make_sysex(did, data):
        sysex = bytearray(PolyD_Cmd.SYX_PREFIX)
        sysex.append(did)
        sysex.extend(data)
        sysex.append(0xF7)
        return sysex

    @staticmethod
    def extract_pattern_from_syx(sysex):
        if len(sysex) != PolyD_Cmd.PATTERN_SYX_SIZE:
            raise PolyD_InvalidArgumentException("Invalid pattern sysex (wrong size)")
        return sysex[15:-1]

    @staticmethod
    def extract_pattern_from_seq(seq):
        if len(seq) != PolyD_Cmd.SEQ_SIZE:
            raise PolyD_InvalidArgumentException("Invalid sequence (wrong size)")
        return seq[len(PolyD_Cmd.SEQ_PREFIX):]

    @staticmethod
    def pattern2Seq(pattern):
        if len(pattern) != PolyD_Cmd.PATTERN_SIZE:
            raise PolyD_InvalidArgumentException("Invalid pattern (wrong size)")
        seq = bytearray(PolyD_Cmd.SEQ_PREFIX)
        seq.extend(pattern)
        return seq

    @staticmethod
    def pattern2syx(did, bank, pattern, pattern_data):
        if len(pattern_data) != PolyD_Cmd.PATTERN_SIZE:
            raise PolyD_InvalidArgumentException("Invalid pattern (wrong size)")
        if bank < 1 or bank > 8:
            raise PolyD_InvalidArgumentException(f"Invalid bank number '{bank}'")
        if pattern < 1 or pattern > 8:
            raise PolyD_InvalidArgumentException(f"Invalid pattern number '{pattern}'")
        sysex = bytearray(PolyD_Cmd.SYX_PREFIX)
        sysex.append(did)
        sysex.append(PolyD_Cmd.SEQ_PATTERN)
        sysex.append(bank - 1)
        sysex.append(pattern - 1)
        sysex.append(0x75)
        sysex.append(0x02)
        sysex.extend(PolyD_Cmd.calc_pattern_checksum(pattern_data))
        sysex.extend(pattern_data)
        sysex.append(0xF7)
        return sysex

    @staticmethod
    def syx2seq(syx):
        pattern_data = PolyD_Cmd.extract_pattern_from_syx(syx)
        return PolyD_Cmd.pattern2Seq(pattern_data)

    @staticmethod
    def seq2syx(did, bank, pattern, seq):
        pattern_data = PolyD_Cmd.extract_pattern_from_seq(seq)
        return PolyD_Cmd.pattern2syx(did, bank, pattern, pattern_data)

    @staticmethod
    def calc_pattern_checksum(pattern_data):
        sum = 0
        for i in range(len(pattern_data)):
            sum += pattern_data[i]
        return (sum & 0x7f, (sum & 0x80) >> 7)
