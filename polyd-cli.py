#! /usr/bin/env python

import argparse

from midiconnection import MidiConnection, MidiException
from polyd import PolyD, PolyD_Config, PolyD_InvalidArgumentException

NAME = 'polyd-cli'
VERSION = 1.0

def first_or_default(arr, pred):
    return next(iter([x for x in arr if pred(x)]), None)

def is_polyd(name):
    return 'POLY D' in name

def dump(version, config):
    print("Firmware version         :", ".".join([str(v) for v in version]))
    print("Device id                :", config.device_id)
    print("MIDI RX Channel          :", config.midi_rx_channel)
    print("MIDI TX Channel          :", config.midi_tx_channel)
    print("MIDI In Transpose        :", config.midi_in_transpose)
    print("Key Velocity of Note On  :", config.note_on_velocity)
    print("Key Velocity of Note Off :", config.note_off_velocity)
    print("Velocity Curve           :", config.velocity_curve)
    print("Key Priority             :", config.key_priority)
    print("Multi Trigger            :", config.multi_trigger)
    print("Pitch Bend Range         :", config.pitch_bend_range)
    print("Modulation Wheel Range   :", config.mod_wheel_range)
    print("Modulation Curve         :", config.modulation_curve)
    print("Note @zero CV            :", config.note_at_zero_cv)
    print("Sync Clock Rate          :", config.sync_clock_rate)
    print("Sync Clock Source        :", config.sync_clock_source)
    print("Local Keyboard Mode      :", config.local_keyboard_mode)
    print("External Clock Polarity  :", config.ext_clock_polarity)
    print("Accent Velocity          :", config.accent_velocity)
    print("MIDI Clock Output        :", config.midi_clock_output)
    print("Pitch Wheel MIDI Output  :", config.pitch_wheel_output)
    print("Mod Wheel MIDI Output    :", config.mod_wheel_output)
    print("Keyboard MIDI Output     :", config.keyboard_output)
    print("After Touch MIDI Output  :", config.after_touch_output)
    print("Sequencer MIDI Output    :", config.sequencer_output)
    print("Arpeggiator MIDI Output  :", config.arpeggiator_output)

def get_range_string(values):
    text = ", ".join([f"\'{v}\'" for v in values])
    text += f" or 0-{len(values)}"
    return text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", help=f"show {NAME}'s version number.", action="store_true")
    parser.add_argument("-l", "--list", help="list the MIDI interfaces.", action="store_true")
    parser.add_argument("-d", "--dump", help="dumps the configuration.", action="store_true")
    parser.add_argument("--id", help="set the device id (0-127)", type=int, default=None)
    parser.add_argument("--rx", help="set MIDI rx channel (1-16)", type=int, default=None)
    parser.add_argument("--tx", help="set MIDI rx channel (1-16)", type=int, default=None)
    parser.add_argument("--in_trans", help="set MIDI in transpose (-12-12)", type=int, default=None)
    parser.add_argument("--vel_on", help="set the note on velocity (0-127)", type=int, default=None)
    parser.add_argument("--vel_off", help="set the note off velocity (0-127)", type=int, default=None)
    parser.add_argument("--vel_curve", help=f"set the velocity curve ({get_range_string(PolyD_Config.CURVES)})", default=None)
    parser.add_argument("--key_prio", help=f"set the key priority ({get_range_string(PolyD_Config.KEY_PRIORITIES)})", default=None)
    parser.add_argument("--multi_trig", help=f"set the multi trigger  ('on', 'off' or 0-1)", default=None)
    parser.add_argument("--pbend_range", help="set the pitch bend range (0-24)", type=int, default=None)
    parser.add_argument("--mod_range", help=f"set the mod wheel range ({get_range_string(PolyD_Config.MOD_RANGES).replace('%', '%%')})", default=None)
    parser.add_argument("--mod_curve", help=f"set the modulation curve ({get_range_string(PolyD_Config.CURVES)})", default=None)
    parser.add_argument("--note_zero", help="set the note at 0 CV (0-127)", type=int, default=None)
    parser.add_argument("--sync_rate", help=f"set the sync clock rate ({get_range_string(PolyD_Config.CLOCKS)})", default=None)
    parser.add_argument("--sync_src", help=f"set the sync clock source ({get_range_string(PolyD_Config.PORTS)})", default=None)
    parser.add_argument("--local", help=f"set the local keyboard mode ('on', 'off' or 0-1)", default=None)
    parser.add_argument("--ext_pol", help=f"set the external clock polarity ({get_range_string(PolyD_Config.POLARITIES)})", default=None)
    parser.add_argument("--acc_vel", help="set the accent velocity (0-127)", type=int, default=None)
    parser.add_argument("--clock_out", help=f"set the MIDI clock output ({get_range_string(PolyD_Config.PORTS)})", default=None)
    parser.add_argument("--pbend_out", help=f"set the pitch wheel MIDI output ({get_range_string(PolyD_Config.PORTS)})", default=None)
    parser.add_argument("--mod_out", help=f"set the mod wheel MIDI output ({get_range_string(PolyD_Config.PORTS)})", default=None)
    parser.add_argument("--key_out", help=f"set the keyboard MIDI output ({get_range_string(PolyD_Config.PORTS)})", default=None)
    parser.add_argument("--at_out", help=f"set the after touch MIDI output ({get_range_string(PolyD_Config.PORTS)})", default=None)
    parser.add_argument("--seq_out", help=f"set the sequencer MIDI output ({get_range_string(PolyD_Config.PORTS)})", default=None)
    parser.add_argument("--arp_out", help=f"set the arpeggiator MIDI output ({get_range_string(PolyD_Config.PORTS)})", default=None)

    args = parser.parse_args()
    if args.list:
        ids = MidiConnection().get_ids()
        for name in ids:
            print("    ", name)
        return
    if args.version:
        print(f"{NAME} Version: {VERSION}")
        return
    args_dict = vars(args)
 
    midi = MidiConnection()
    in_id = first_or_default(midi.get_input_ids(), is_polyd)
    out_id = first_or_default(midi.get_output_ids(), is_polyd)
    if in_id is None or out_id is None:
        print("No Poly D found.")
        return
    if not midi.connect_write(out_id):
        print(f"Could not connect to MIDI device {out_id}.")
        return
    if not midi.connect_read(in_id):
        print(f"Could not connect to MIDI device {in_id}.")
        return

    polyd = PolyD(midi)
    version = polyd.get_version()
    if version != (1,1,0):
        print()
        print("Warning: This program is tested with firmware 1.1.0 only.")
        print("         It might not work as intended on other versions.")
        print()
        exit(1)

    handlers = {
        "id":          polyd.set_id,
        "rx":          polyd.set_rx_channel,
        "tx":          polyd.set_tx_channel,
        "in_trans":    polyd.set_in_transpose,
        "vel_on":      polyd.set_velocity_on,
        "vel_off":     polyd.set_velocity_off,
        "vel_curve":   polyd.set_velocity_curve,
        "key_prio":    polyd.set_key_priority,
        "multi_trig":  polyd.set_multi_trig,
        "pbend_range": polyd.set_pbend_range,
        "mod_range":   polyd.set_mod_range,
        "mod_curve":   polyd.set_mod_curve,
        "note_zero":   polyd.set_note_zero,
        "sync_rate":   polyd.set_sync_rate,
        "sync_src":    polyd.set_sync_source,
        "local":       polyd.set_local_mode,
        "ext_pol":     polyd.set_ext_clock_polarity,
        "acc_vel":     polyd.set_accent_velocity,
        "clock_out":   polyd.set_clock_out,
        "pbend_out":   polyd.set_pbend_out,
        "mod_out":     polyd.set_mod_out,
        "key_out":     polyd.set_key_out,
        "at_out":      polyd.set_at_out,
        "seq_out":     polyd.set_seq_out,
        "arp_out":     polyd.set_arp_out
    }

    try:
        for key,func in handlers.items():
            if key in args_dict:
                value = args_dict[key]
                if value is not None:
                    func(value)
            else:
                raise PolyD_InvalidArgumentException(f"Unknown argument {key}")
        
        if args.dump:
            config = polyd.get_config()
            dump(version, config)

    except MidiException as exc:
        print("Error:", exc.message)
    
    midi.disconnect()

if __name__ == "__main__":
    main()
