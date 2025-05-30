import re
import time

from midiconnection import MidiException
from polyd_config import PolyD_Config
from polyd_cmd import PolyD_Cmd
from polyd_exc import PolyD_InvalidArgumentException, PolyD_MidiException

class PolyD:
    __BOOL_TEXTS = ['off', 'on', 'no', 'yes', 'false', 'true']

    def __init__(self, midi):
        self.__midi = midi
        self.__config = None

    def get_config(self):
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.GET_SETTINGS ])
        answer = self.__midi.sysex_communicate(sysex)
        self.__config = PolyD_Config(bytes(answer.bytes()))
        return self.__config

    def get_pattern(self, bank, pattern):
        if bank is None or pattern is None:
            raise PolyD_InvalidArgumentException("'bank' and 'pattern' must be specified.")
        self.__check_range(bank, 1, 8, "bank")
        self.__check_range(pattern, 1, 8, "pattern")
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.GET_SEQ_PATTERN, bank-1, pattern-1 ])
        return bytes(self.__midi.sysex_communicate(sysex).bytes())

    def set_pattern(self, sysex, bank, pattern):
        if bank is not None or pattern is not None:
            if bank is None or pattern is None:
                raise PolyD_InvalidArgumentException("'bank' and 'pattern' must be specified.")
            self.__check_range(bank, 1, 8, "bank")
            self.__check_range(pattern, 1, 8, "pattern")
            sysex = bytearray(sysex)
            sysex[9] = bank - 1
            sysex[10] = pattern - 1
        self.__midi.write(sysex)

    def get_version(self):
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.GET_FW_VERSION, 0 ])
        answer = self.__midi.sysex_communicate(sysex)
        return answer.data[-3:]

    def set_id(self, value):
        name = "device id"
        self.__check_range(value, 0, 127, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_DEVICE_ID, value ])
        self.send_config_sysex(sysex, name)

    def set_rx_channel(self, rx):
        name = "MIDI rx channel"
        if self.__normalize_text(rx) == 'all':
            rx = 16
        else:
            rx = int(rx) - 1
        self.__check_range(rx, 0, 16, name)
        tx = self.__cached_config.midi_tx_channel_value
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_MIDI_CHANNELS, 1, tx, rx ])
        self.send_config_sysex(sysex, name)

    def set_tx_channel(self, tx):
        name = "MIDI tx channel"
        tx = int(tx) - 1
        self.__check_range(tx, 0, 15, name)
        rx = self.__cached_config.midi_rx_channel_value
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_MIDI_CHANNELS, 1, tx, rx ])
        self.send_config_sysex(sysex, name)

    def set_in_transpose(self, value):
        name = "MIDI in transpose value"
        self.__check_range(value, -12, 12, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_MIDI_IN_TRANSPOSE, value ])
        self.send_config_sysex(sysex, name)

    def set_velocity_on(self, vel_on):
        name = "note on velocity"
        self.__check_range(vel_on, 0, 127, name)
        vel_off = self.__cached_config.note_off_velocity
        vel_curve = self.__cached_config.velocity_curve_value
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_VELOCITY_INFO, vel_on, vel_off, vel_curve ])
        self.send_config_sysex(sysex, name)

    def set_velocity_off(self, vel_off):
        name = "note off velocity"
        self.__check_range(vel_off, 0, 127, name)
        vel_on = self.__cached_config.note_on_velocity
        vel_curve = self.__cached_config.velocity_curve_value
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_VELOCITY_INFO, vel_on, vel_off, vel_curve ])
        self.send_config_sysex(sysex, name)

    def set_velocity_curve(self, vel_curve_text):
        name = "velocity curve"
        vel_curve = self.__text_to_value(vel_curve_text, PolyD_Config.CURVES, name)
        vel_on = self.__cached_config.note_on_velocity
        vel_off = self.__cached_config.note_off_velocity
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_VELOCITY_INFO, vel_on, vel_off, vel_curve ])
        self.send_config_sysex(sysex, name)

    def set_key_priority(self, key_prio_text):
        name = "key priority"
        key_prio = self.__text_to_value(key_prio_text, PolyD_Config.KEY_PRIORITIES, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_KEY_PRIORITY, key_prio ])
        self.send_config_sysex(sysex, name)

    def set_multi_trig(self, text):
        name = "multi trigger"
        value = self.__text_to_value(text, self.__BOOL_TEXTS, name)
        value = value % 2
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_MULTI_TRIGGER, value, 0 ])
        self.send_config_sysex(sysex, name)

    def set_pbend_range(self, value):
        name = "pitch bend range"
        self.__check_range(value, 0, 24, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_PITCH_BEND_RANGE, value, 0 ])
        self.send_config_sysex(sysex, name)

    def set_mod_range(self, text):
        name = "mod wheel range"
        value = self.__text_to_value(text, PolyD_Config.MOD_RANGES, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_MOD_WHEEL_RANGE, value ])
        self.send_config_sysex(sysex, name)

    def set_mod_curve(self, text):
        name = "modulation curve"
        value = self.__text_to_value(text, PolyD_Config.CURVES, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_MOD_CURVE, value ])
        self.send_config_sysex(sysex, name)

    def set_note_zero(self, value):
        name = "note at 0 CV"
        self.__check_range(value, 0, 127, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_NOTE_AT_ZERO, value ])
        self.send_config_sysex(sysex, name)

    def set_sync_rate(self, text):
        name = "sync clock rate"
        value = self.__text_to_value(text, PolyD_Config.CLOCKS, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_SYNC_RATE, value ])
        self.send_config_sysex(sysex, name)

    def set_sync_source(self, text):
        name = "sync clock source"
        value = self.__text_to_value(text, PolyD_Config.SYNC_PORTS, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_CLOCK_SOURCE, value ])
        self.send_config_sysex(sysex, name)

    def set_local_mode(self, text):
        name = "local keyboard mode"
        value = self.__text_to_value(text, self.__BOOL_TEXTS, name)
        value = (value % 2) ^ 1 # Invert, because 0 means 'on'
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_LOCAL_MODE, value ])
        self.send_config_sysex(sysex, name)

    def set_ext_clock_polarity(self, text):
        name = "external clock polarity"
        value = self.__text_to_value(text, PolyD_Config.POLARITIES, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_EXT_CLOCK_POLARITY, value ])
        self.send_config_sysex(sysex, name)

    def set_accent_velocity(self, value):
        name = "accen velocity"
        self.__check_range(value, 0, 127, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_ACCENT_VELOCITY, value ])
        self.send_config_sysex(sysex, name)

    def set_clock_out(self, text):
        name = "MIDI clock output"
        value = self.__text_to_value(text, PolyD_Config.PORTS, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_CLOCK_OUT, value ])
        self.send_config_sysex(sysex, name)

    def set_pbend_out(self, text):
        name = "pitch wheel MIDI output"
        value = self.__text_to_value(text, PolyD_Config.PORTS, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_PITCH_BEND_OUT, value ])
        self.send_config_sysex(sysex, name)

    def set_mod_out(self, text):
        name = "modulation wheel MIDI output"
        value = self.__text_to_value(text, PolyD_Config.PORTS, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_MOD_WHEEL_OUT, value ])
        self.send_config_sysex(sysex, name)

    def set_key_out(self, text):
        name = "keyboard MIDI output"
        value = self.__text_to_value(text, PolyD_Config.PORTS, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_KEY_OUT, value ])
        self.send_config_sysex(sysex, name)

    def set_at_out(self, text):
        name = "after touch MIDI output"
        value = self.__text_to_value(text, PolyD_Config.PORTS, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_AFTER_TOUCH_OUT, value ])
        self.send_config_sysex(sysex, name)

    def set_seq_out(self, text):
        name = "sequencer MIDI output"
        value = self.__text_to_value(text, PolyD_Config.PORTS, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_SEQ_OUT, value ])
        self.send_config_sysex(sysex, name)

    def set_arp_out(self, text):
        name = "arpeggiator MIDI output"
        value = self.__text_to_value(text, PolyD_Config.PORTS, name)
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.SET_ARP_OUT, value ])
        self.send_config_sysex(sysex, name)

    def factory_restore(self):
        name = "factory restore"
        sysex = PolyD_Cmd.make_sysex(0, [ PolyD_Cmd.RESTORE_FACTORY_SETTINGS ])
        self.send_config_sysex(sysex, name)

    def send_config_sysex(self, sysex, name):
        if sysex[0] != 0xF0 or sysex[-1] != 0xF7:
            raise PolyD_MidiException("Invalid sysex data")
        answer = self.__midi.sysex_communicate(sysex)
        if answer.data[-2] != 0:
            raise PolyD_MidiException(f"Could not set the {name}")
        self._config = None

    def send_pattern_sysex(self, sysex):
        if sysex[0] != 0xF0 or sysex[-1] != 0xF7:
            raise PolyD_MidiException("Invalid sysex data")
        self.__midi.write(sysex)
        # Wait shortly for an answer. No answer means that erverything is ok.
        # Otherwise an error response is sent.
        # Without waiting here setting sequences does not work reliably, because
        # the Poly-D reports an error as well when the next sysex packet arrives
        # too soon after this one.
        time.sleep(0.1)
        answer = self.try_read()
        if  answer is not None:
            raise PolyD_MidiException("Could not set pattern")

    def try_read(self):
        return self.__midi.try_read()

    def __check_range(self, value, min, max, name):
        if value < min or value > max:
            raise PolyD_InvalidArgumentException(f"Invalid {name} '{value}'")

    def __text_to_value(self, text, allowed, name):
        value = self.__get_value(text, allowed)
        if value < 0 or value >= len(allowed):
            raise PolyD_InvalidArgumentException(f"Invalid {name} '{vtext}'")
        return value

    @property
    def __cached_config(self):
        if self.__config is None:
            self.get_config()
        return self.__config

    @staticmethod
    def __get_value(text, values):
        text = PolyD.__normalize_text(text)
        if re.match(r'\d+$', text):
            return int(text)
        for i in range(0, len(values)):
            if text in PolyD.__normalize_text(values[i]):
                return i
        return -1

    @staticmethod
    def __normalize_text(value):
        text = str(value)
        return re.sub(r'\s+', '', text.lower())
