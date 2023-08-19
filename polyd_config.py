class PolyD_Config:
    __OFFSET = 9
    CURVES = [ 'soft', 'medium', 'hard' ]
    KEY_PRIORITIES = [ 'low', 'high', 'last' ]
    CLOCKS = [ '1 PPS', '2 PPQ', '24 PPQ', '48 PPQ' ]
    PORTS = [ 'off', 'DIN', 'USB', 'both' ]
    POLARITIES = [ 'falling', 'rising' ]
    MOD_RANGES = [ '20%', '50%', '100%', '200%', '300%' ]

    def __init__(self, data):
        self.__data = data

    @property
    def device_id(self):
        return self.__data[self.__OFFSET + 0]

    @property
    def midi_rx_channel(self):
        return self.__data[self.__OFFSET + 1] + 1

    @property
    def midi_tx_channel(self):
        return self.__data[self.__OFFSET + 2] + 1

    @property
    def midi_in_transpose(self):
        return self.__data[self.__OFFSET + 3] - 12

    @property
    def note_on_velocity(self):
        return self.__data[self.__OFFSET + 4]

    @property
    def note_off_velocity(self):
        return self.__data[self.__OFFSET + 5]

    @property
    def velocity_curve_value(self):
        return self.__data[self.__OFFSET + 6]

    @property
    def velocity_curve(self):
        return self.CURVES[self.velocity_curve_value]

    @property
    def key_priority(self):
        return self.KEY_PRIORITIES[self.__data[self.__OFFSET + 7]]

    @property
    def multi_trigger(self):
        if self.__data[self.__OFFSET + 8] != 0:
            return "on"
        else:
            return "off"

    @property
    def pitch_bend_range(self):
        return self.__data[self.__OFFSET + 9]

    @property
    def mod_wheel_range(self):
        return self.__data[self.__OFFSET + 10]

    @property
    def modulation_curve(self):
        return self.CURVES[self.__data[self.__OFFSET + 11]]

    @property
    def note_at_zero_cv(self):
        return self.__data[self.__OFFSET + 12]

    @property
    def sync_clock_rate(self):
        return self.CLOCKS[self.__data[self.__OFFSET + 13]]

    @property
    def sync_clock_source(self):
        return self.PORTS[self.__data[self.__OFFSET + 14]]

    @property
    def local_keyboard_mode(self):
        if self.__data[self.__OFFSET + 15] != 0:
            return "off"
        else:
            return "on"

    @property
    def ext_clock_polarity(self):
        return self.POLARITIES[self.__data[self.__OFFSET + 16]]

    @property
    def accent_velocity(self):
        return self.__data[self.__OFFSET + 17]

    @property
    def midi_clock_output(self):
        return self.PORTS[self.__data[self.__OFFSET + 18]]

    @property
    def pitch_wheel_output(self):
        return self.PORTS[self.__data[self.__OFFSET + 19]]

    @property
    def mod_wheel_output(self):
        return self.PORTS[self.__data[self.__OFFSET + 20]]

    @property
    def keyboard_output(self):
        return self.PORTS[self.__data[self.__OFFSET + 21]]

    @property
    def after_touch_output(self):
        return self.PORTS[self.__data[self.__OFFSET + 22]]

    @property
    def sequencer_output(self):
        return self.PORTS[self.__data[self.__OFFSET + 23]]

    @property
    def arpeggiator_output(self):
        return self.PORTS[self.__data[self.__OFFSET + 24]]

    @property
    def sysex(self):
        return self.__data
