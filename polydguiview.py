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
        self.raise_events = True
        super().__init__(**kwargs)

    def on_kv_post(self, _):
        self._show_config()
        self.dev_id.bind(text=lambda _,v: self._value_changed(self._id_changed, v))
        self.rx.bind(text=lambda _,v: self._value_changed(self._rx_changed, v))
        self.tx.bind(text=lambda _,v: self._value_changed(self._tx_changed, v))
        self.in_transpose.bind(text=lambda _,v: self._value_changed(self._in_transpose_changed, v))
        self.velocity_on.velocity_changed += lambda v: self._value_changed(self._velocity_on_changed, v)
        self.velocity_off.velocity_changed += lambda v: self._value_changed(self._velocity_off_changed, v)
        self.velocity_curve.bind(text=lambda _,v: self._value_changed(self._velocity_curve_changed, v))
        self.key_priority.bind(text=lambda _,v: self._value_changed(self._key_priority_changed, v))
        self.multi_trig.bind(text=lambda _,v: self._value_changed(self._multi_trig_changed, v))
        self.pitch_bend.bind(text=lambda _,v: self._value_changed(self._pitch_bend_changed, v))
        self.mod_range.bind(text=lambda _,v: self._value_changed(self._mod_range_changed, v))
        self.modulation_curve.bind(text=lambda _,v: self._value_changed(self._modulation_curve_changed, v))
        self.note_zero.bind(text=lambda _,v: self._value_changed(self._note_zero_changed, v))
        self.sync_rate.bind(text=lambda _,v: self._value_changed(self._sync_rate_changed, v))
        self.sync_source.bind(text=lambda _,v: self._value_changed(self._sync_source_changed, v))
        self.ext_clock_pol.bind(text=lambda _,v: self._value_changed(self._ext_clock_pol_changed, v))
        self.accent_velocity.bind(text=lambda _,v: self._value_changed(self._accent_velocity_changed, v))
        self.local_control.bind(text=lambda _,v: self._value_changed(self._local_control_changed, v))
        self.clock_out.bind(text=lambda _,v: self._value_changed(self._clock_out_changed, v))
        self.pbend_out.bind(text=lambda _,v: self._value_changed(self._pbend_out_changed, v))
        self.modwheel_out.bind(text=lambda _,v: self._value_changed(self._modwheel_out_changed, ))
        self.key_out.bind(text=lambda _,v: self._value_changed(self._key_out_changed, v))
        self.at_out.bind(text=lambda _,v: self._value_changed(self._at_out_changed, v))
        self.seq_out.bind(text=lambda _,v: self._value_changed(self.seq_out_changed, v))
        self.arp_out.bind(text=lambda _,v: self._value_changed(self._arp_out_changed, v))

    def restore_factory_settings(self):
        print("Restore Factory Settings")
        self.polyd.factory_restore()
        self._show_config()

    def _show_config(self):
        self.raise_events = False
        self.version = ".".join([str(v) for v in self.polyd.get_version()])
        config = self.polyd.get_config()
        self.dev_id.text = str(config.device_id)
        self.rx.text = self.midi_in_channels[config.midi_rx_channel_value]
        self.tx.text = self.midi_out_channels[config.midi_tx_channel_value]
        self.in_transpose.text = self.in_transposes[config.midi_in_transpose + 12]
        self.velocity_on.set_velocity(config.note_on_velocity)
        self.velocity_off.set_velocity(config.note_off_velocity)
        self.velocity_curve.text = config.velocity_curve
        self.key_priority.text = config.key_priority
        self.multi_trig.text = config.multi_trigger
        self.pitch_bend.text = self.pitch_bends[config.pitch_bend_range]
        self.mod_range.text = self.mod_ranges[config.mod_wheel_range]
        self.modulation_curve.text = config.modulation_curve
        self.note_zero.text = str(config.note_at_zero_cv)
        self.sync_rate.text = config.sync_clock_rate
        self.sync_source.text = config.sync_clock_source
        self.ext_clock_pol.text = config.ext_clock_polarity
        self.accent_velocity.text = str(config.accent_velocity)
        self.local_control.text = config.local_keyboard_mode
        self.clock_out.text = config.midi_clock_output
        self.pbend_out.text = config.pitch_wheel_output
        self.modwheel_out.text = config.mod_wheel_output
        self.key_out.text = config.keyboard_output
        self.at_out.text = config.after_touch_output
        self.seq_out.text = config.sequencer_output
        self.arp_out.text = config.arpeggiator_output
        self.raise_events = True

    def _value_changed(self, func, value):
        if not self.raise_events:
            return
        func(value)

    def _id_changed(value):
        if value == "":
            return
        id = int(value)
        if id < 0 or id > 127:
            return
        self.polyd.set_id(id)
        print("ID changed:", id)

    def _rx_changed(self, value):
        channel = self.midi_in_channels.index(value) + 1
        if channel == 17:
            channel = 'all'
        print("RX changed:", channel)
        self.polyd.set_rx_channel(channel)
    
    def _tx_changed(self, value):
        channel = self.midi_out_channels.index(value) + 1
        print("TX changed:", channel)
        self.polyd.set_tx_channel(channel)

    def _in_transpose_changed(self, value):
        in_transpose = int(value)
        print("In Transpose changed:", in_transpose)
        self.polyd.set_in_transpose(in_transpose)
    
    def _velocity_on_changed(self, velocity):
        print("Velocity On:", velocity)
        self.polyd.set_velocity_on(velocity)

    def _velocity_off_changed(self, velocity):
        print("Velocity Off:", velocity)
        self.polyd.set_velocity_off(velocity)

    def _velocity_curve_changed(self, value):
        print("Velocity curve:", value)
        self.polyd.set_velocity_curve(value)

    def _key_priority_changed(self, value):
        print("Key priority:", value)
        self.polyd.set_key_priority(value)

    def _multi_trig_changed(self, value):
        print("Multi trigger:", value)
        self.polyd.set_multi_trig(value)

    def _pitch_bend_changed(self, value):
        range = self.pitch_bends.index(value)
        print("Pitch bend range:", range)
        self.polyd.set_pbend_range(range)

    def _mod_range_changed(self, value):
        print("Mod wheel range:", value)
        self.polyd.set_mod_range(value)

    def _modulation_curve_changed(self, value):
        print("Modulation curve:", value)
        self.polyd.set_mod_curve(value)

    def _note_zero_changed(self, value):
        if value == "":
            return
        note = int(value)
        if note < 0 or note > 127:
            return
        print("Note @zero CV:", note)
        self.polyd.set_note_zero(note)

    def _sync_rate_changed(self, value):
        print("Sync Rate:", value)
        self.polyd.set_sync_rate(value)

    def _sync_source_changed(self, value):
        print("Sync Source:", value)
        self.polyd.set_sync_source(value)

    def _ext_clock_pol_changed(self, value):
        print("Ext. Clock Polarity:", value)
        self.polyd.set_ext_clock_polarity(value)

    def _accent_velocity_changed(self, value):
        if value == "":
            return
        velo = int(value)
        if velo < 0 or velo > 127:
            return
        print("Accent Velocity:", velo)
        self.polyd.set_accent_velocity(velo)

    def _local_control_changed(self, value):
        print("Local Control:", value)
        self.polyd.set_local_mode(value)

    def _clock_out_changed(self, value):
        print("Clock Out", value)
        self.polyd.set_clock_out(value)

    def _pbend_out_changed(self, value):
        print("Pitchbend Out", value)
        self.polyd.set_pbend_out(value)
    
    def _modwheel_out_changed(self, value):
        print("Modulation Out", value)
        self.polyd.set_mod_out(value)
    
    def _key_out_changed(self, value):
        print("Keyboard Out", value)
        self.polyd.set_key_out(value)
    
    def _at_out_changed(self, value):
        print("After Touch Out", value)
        self.polyd.set_at_out(value)
    
    def seq_out_changed(self, value):
        print("Sequencer Out", value)
        self.polyd.set_seq_out(value)
    
    def _arp_out_changed(self, value):
        print("Arpeggiator Out", value)
        self.polyd.set_arp_out(value)
