from delegate import Delegate

from polyd_config import PolyD_Config

from kivy.properties import NumericProperty, ObjectProperty, StringProperty

from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

class HBox(BoxLayout):
    pass

class OptionButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouseover)

    def on_mouseover(self, window, pos):
        if self.collide_point(*self.to_widget(*pos)):
            self.background_color = (0.6, 0.6, 0.6, 1)
        else:
            self.background_color = (0.7, 0.7, 0.7, 1)

class IntInput(TextInput):
    min_value = NumericProperty(0)
    max_value = NumericProperty(127)
    error_color = (1, 0.65, 0.65, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def insert_text(self, substring, from_undo=False):
        s = "".join([c for c in substring if c in '0123456789'])
        return super().insert_text(s, from_undo=from_undo)

    def on_text(self, textinput, text):
        if text == "":
            textinput.background_color = self.error_color
            return
        num = int(text)
        if num < self.min_value or num > self.max_value:
            textinput.background_color = self.error_color
        else:
            textinput.background_color = (1,1,1,1)

class VelocityEditor(HBox):
    mode = ObjectProperty()
    value = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.values = ("Dynamic", "Constant")
        self.velocity = 0
        self.velocity_changed = Delegate()
        self.raise_change_events = True

    def on_kv_post(self, _):
        self.mode.values = self.values
        self.mode.bind(text=self.on_mode_changed)
        self.value.bind(text=self.on_text_changed)

    def on_mode_changed(self, _, value):
        if value == self.values[0]:
            self.value.disabled = True
            self.change_velocity(0)
        else:
            self.value.disabled = False
            text = self.value.text
            if text == '':
                return
            velocity = int(text)
            if velocity >= 1 and velocity <= 127:
                self.change_velocity(velocity)

    def on_text_changed(self, _, value):
        if value == '':
            return
        velocity = int(value)
        if velocity >= 1 and velocity <= 127:
            self.change_velocity(velocity)

    def change_velocity(self, velocity):
        if not self.raise_change_events or velocity == self.velocity:
            return
        self.velocity = velocity
        self.velocity_changed(velocity)

    def set_velocity(self, velocity):
        self.raise_change_events = False
        if velocity == 0:
            self.value.disabled = True
            self.value.text = "1"
            self.mode.text = self.values[0]
        else:
            self.value.disabled = False
            self.value.text = str(velocity)
            self.mode.text = self.values[1]
        self.velocity = velocity
        self.raise_change_events = True

class PolyDGuiView(BoxLayout):
    version = StringProperty()
    dev_id = ObjectProperty()
    rx = ObjectProperty()
    tx = ObjectProperty()
    in_transpose = ObjectProperty()
    velocity_on = ObjectProperty()
    velocity_off = ObjectProperty()
    velocity_curve = ObjectProperty()
    key_priority = ObjectProperty()
    multi_trig = ObjectProperty()
    pitch_bend = ObjectProperty()
    mod_range = ObjectProperty()
    modulation_curve = ObjectProperty()
    note_zero = ObjectProperty()
    sync_rate = ObjectProperty()
    sync_source = ObjectProperty()
    ext_clock_pol = ObjectProperty()
    accent_velocity = ObjectProperty()
    local_control = ObjectProperty()
    clock_out = ObjectProperty()
    pbend_out = ObjectProperty()
    modwheel_out = ObjectProperty()
    key_out = ObjectProperty()
    at_out = ObjectProperty()
    seq_out = ObjectProperty()
    arp_out = ObjectProperty()

    midi_in_channels = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', 'All')
    midi_out_channels = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16')
    in_transposes = ('-12', '-11', '-10', '-9', '-8', '-7', '-6', '-5', '-4', '-3', '-2', '-1',
                     '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12')
    pitch_bends = ( '0','1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
                    '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24')
    velocity_curves = PolyD_Config.CURVES
    key_priorities = PolyD_Config.KEY_PRIORITIES
    off_on = PolyD_Config.OFF_ON
    mod_ranges = PolyD_Config.MOD_RANGES
    modulation_curves = PolyD_Config.CURVES
    clocks = PolyD_Config.CLOCKS
    sync_ports = PolyD_Config.SYNC_PORTS
    polarities = PolyD_Config.POLARITIES
    ports = PolyD_Config.PORTS

    def __init__(self, polyd, **kwargs):
        self.polyd = polyd
        super().__init__(**kwargs)

    def on_kv_post(self, _):
        self.version = ".".join([str(v) for v in self.polyd.get_version()])
        config = self.polyd.get_config()
        self._setup_widget(self.dev_id, str(config.device_id), self._id_changed)
        self._setup_widget(self.rx, self.midi_in_channels[config.midi_rx_channel_value], self._rx_changed)
        self._setup_widget(self.tx, self.midi_out_channels[config.midi_tx_channel_value], self._tx_changed)
        self._setup_widget(self.in_transpose, self.in_transposes[config.midi_in_transpose + 12], self._in_transpose_changed)
        self.velocity_on.set_velocity(config.note_on_velocity)
        self.velocity_on.velocity_changed += self._velocity_on_changed
        self.velocity_off.set_velocity(config.note_off_velocity)
        self.velocity_off.velocity_changed += self._velocity_off_changed
        self._setup_widget(self.velocity_curve, config.velocity_curve, self._velocity_curve_changed)
        self._setup_widget(self.key_priority, config.key_priority, self._key_priority_changed)
        self._setup_widget(self.multi_trig, config.multi_trigger, self._multi_trig_changed)
        self._setup_widget(self.pitch_bend, self.pitch_bends[config.pitch_bend_range],self._pitch_bend_changed)
        self._setup_widget(self.mod_range, self.mod_ranges[config.mod_wheel_range], self._mod_range_changed)
        self._setup_widget(self.modulation_curve, config.modulation_curve, self._modulation_curve_changed)
        self._setup_widget(self.note_zero, str(config.note_at_zero_cv), self._note_zero_changed)
        self._setup_widget(self.sync_rate, config.sync_clock_rate, self._sync_rate_changed)
        self._setup_widget(self.sync_source, config.sync_clock_source, self._sync_source_changed)
        self._setup_widget(self.ext_clock_pol, config.ext_clock_polarity, self._ext_clock_pol_changed)
        self._setup_widget(self.accent_velocity, str(config.accent_velocity), self._accent_velocity_changed)
        self._setup_widget(self.local_control, config.local_keyboard_mode, self._local_control_changed)
        self._setup_widget(self.clock_out, config.midi_clock_output, self._clock_out_changed)
        self._setup_widget(self.pbend_out, config.pitch_wheel_output, self._pbend_out_changed)
        self._setup_widget(self.modwheel_out, config.mod_wheel_output, self._modwheel_out_changed)
        self._setup_widget(self.key_out, config.keyboard_output, self._key_out_changed)
        self._setup_widget(self.at_out, config.after_touch_output, self._at_out_changed)
        self._setup_widget(self.seq_out, config.sequencer_output, self.seq_out_changed)
        self._setup_widget(self.arp_out, config.arpeggiator_output, self._arp_out_changed)

    def _setup_widget(self, widget, text, callback):
        widget.text = text
        widget.bind(text=callback)
    
    def _id_changed(self, _, value):
        if value == "":
            return
        id = int(value)
        if id < 0 or id > 127:
            return
        self.polyd.set_id(id)
        print("ID changed:", id)

    def _rx_changed(self, _, value):
        channel = self.midi_in_channels.index(value) + 1
        if channel == 17:
            channel = 'all'
        print("RX changed:", channel)
        self.polyd.set_rx_channel(channel)
    
    def _tx_changed(self, _, value):
        channel = self.midi_out_channels.index(value) + 1
        print("TX changed:", channel)
        self.polyd.set_tx_channel(channel)

    def _in_transpose_changed(self, _, value):
        in_transpose = int(value)
        print("In Transpose changed:", in_transpose)
        self.polyd.set_in_transpose(in_transpose)
    
    def _velocity_on_changed(self, velocity):
        print("Velocity On:", velocity)
        self.polyd.set_velocity_on(velocity)

    def _velocity_off_changed(self, velocity):
        print("Velocity Off:", velocity)
        self.polyd.set_velocity_off(velocity)

    def _velocity_curve_changed(self, _, value):
        print("Velocity curve:", value)
        self.polyd.set_velocity_curve(value)

    def _key_priority_changed(self, _, value):
        print("Key priority:", value)
        self.polyd.set_key_priority(value)

    def _multi_trig_changed(self, _, value):
        print("Multi trigger:", value)
        self.polyd.set_multi_trig(value)

    def _pitch_bend_changed(self, _, value):
        range = self.pitch_bends.index(value)
        print("Pitch bend range:", range)
        self.polyd.set_pbend_range(range)

    def _mod_range_changed(self, _, value):
        print("Mod wheel range:", value)
        self.polyd.set_mod_range(value)

    def _modulation_curve_changed(self, _, value):
        print("Modulation curve:", value)
        self.polyd.set_mod_curve(value)

    def _note_zero_changed(self, _, value):
        if value == "":
            return
        note = int(value)
        if note < 0 or note > 127:
            return
        print("Note @zero CV:", note)
        self.polyd.set_note_zero(note)

    def _sync_rate_changed(self, _, value):
        print("Sync Rate:", value)
        self.polyd.set_sync_rate(value)

    def _sync_source_changed(self, _, value):
        print("Sync Source:", value)
        self.polyd.set_sync_source(value)

    def _ext_clock_pol_changed(self, _, value):
        print("Ext. Clock Polarity:", value)
        self.polyd.set_ext_clock_polarity(value)

    def _accent_velocity_changed(self, _, value):
        if value == "":
            return
        velo = int(value)
        if velo < 0 or velo > 127:
            return
        print("Accent Velocity:", velo)
        self.polyd.set_accent_velocity(velo)

    def _local_control_changed(self, _, value):
        print("Local Control:", value)
        self.polyd.set_local_mode(value)

    def _clock_out_changed(self, _, value):
        print("Clock Out", value)
        self.polyd.set_clock_out(value)

    def _pbend_out_changed(self, _, value):
        print("Pitchbend Out", value)
        self.polyd.set_pbend_out(value)
    
    def _modwheel_out_changed(self, _, value):
        print("Modulation Out", value)
        self.polyd.set_mod_out(value)
    
    def _key_out_changed(self, _, value):
        print("Keyboard Out", value)
        self.polyd.set_key_out(value)
    
    def _at_out_changed(self, _, value):
        print("After Touch Out", value)
        self.polyd.set_at_out(value)
    
    def seq_out_changed(self, _, value):
        print("Sequencer Out", value)
        self.polyd.set_seq_out(value)
    
    def _arp_out_changed(self, _, value):
        print("Arpeggiator Out", value)
        self.polyd.set_arp_out(value)
