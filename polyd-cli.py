#! /usr/bin/env python

import argparse
import sys
import zipfile

from midiconnection import MidiConnection, MidiException
from polyd_cmd import PolyD_Cmd
from polyd_exc import PolyD_Exception, PolyD_InvalidArgumentException
from polyd_config import PolyD_Config
from polyd import PolyD 

NAME = 'polyd-cli'
VERSION = 1.5

CONFIGNAME = "config.syx"
CONFIGSIZE = 35

def get_range_string(values):
    text = ", ".join([f"\'{v}\'" for v in values])
    text += f" or 0-{len(values)}"
    return text

def first_or_default(arr, pred):
    return next(iter([x for x in arr if pred(x)]), None)

def is_polyd(searched_name, port_name):
    return searched_name in port_name

def pattern_name(bank, pattern):
    return f"b{bank}p{pattern}.seq"


def save_single_pattern(polyd, filename, bank, pattern):
    # Write single pattern into a seq file
    sysex = polyd.get_pattern(bank, pattern)
    seq = PolyD_Cmd.syx2seq(sysex)
    with open(filename, "wb") as fp:
        fp.write(seq)

def save_config(polyd, filename):
    # Write the configuration into a syx file
    config = polyd.get_config()
    with open(filename, "wb") as fp:
        fp.write(config.sysex)

def save_all(polyd, filename):
    # Write a zip file with the configuration and all patterns
    with zipfile.ZipFile(filename, "w") as zip:
        config = polyd.get_config()
        zip.writestr(CONFIGNAME, config.sysex)

        for bank in range(1, 9):
            for pattern in range(1,9):
                sysex = polyd.get_pattern(bank, pattern)
                seq = PolyD_Cmd.syx2seq(sysex)
                zip.writestr(pattern_name(bank, pattern), seq)

def save(polyd, filename, config_only, patterns_only, bank, pattern):
    if bank is not None and pattern is not None:
        save_single_pattern(polyd, filename, bank, pattern)
    elif config_only:
        save_config(polyd, filename)
    else:
        save_all(polyd, filename)

def restore_pattern_sysex(polyd, sysex, bank, pattern):
    if bank is not None:
        sysex[9] = bank - 1
    if pattern is not None:
        sysex[10] = pattern - 2
    polyd.send_pattern_sysex(sysex)

def restore_seq(polyd, seq, bank, pattern):
    if bank is None or pattern is None:
        raise PolyD_InvalidArgumentException("Pattern and/or Bank argument missing.")
    sysex = PolyD_Cmd.seq2syx(0, bank, pattern, seq)
    polyd.send_pattern_sysex(sysex)

def restore_zip(polyd, filename, config_only, patterns_only):
    with zipfile.ZipFile(filename, "r") as zip:
        entries = zip.namelist()
        if CONFIGNAME in entries and not patterns_only:
            sys.stdout.write("Restoring configuration\r")
            sys.stdout.flush()
            config = zip.read(CONFIGNAME)
            polyd.send_config_sysex(config, "configuration")
        if not config_only:
            for bank in range(1, 9):
                for pattern in range(1,9):
                    name = pattern_name(bank, pattern)
                    if name in entries:
                        sys.stdout.write(f"Restoring pattern {bank} {pattern}  \r")
                        sys.stdout.flush()
                        seq = zip.read(name)
                        restore_seq(polyd, seq, bank, pattern)

def restore_file(polyd, filename, config_only, patterns_only, bank, pattern):
    with open(filename, "rb") as fp:
        data = fp.read()
    if len(data) == CONFIGSIZE:
        if not patterns_only:
            polyd.send_config_sysex(data, "configuration")
    elif len(data) == PolyD_Cmd.PATTERN_SYX_SIZE:
        if not config_only:
            restore_pattern_sysex(polyd, data, bank, pattern)
    elif len(data) == PolyD_Cmd.SEQ_SIZE:
        if not config_only:
            restore_seq(polyd, data, bank, pattern)
    else:
        raise PolyD_Exception(f"File '{filename}' is no known Poly D config file.")

def restore(polyd, filename, config_only, patterns_only, bank, pattern):
    if zipfile.is_zipfile(filename):
        restore_zip(polyd, filename, config_only, patterns_only)
    else:
        restore_file(polyd, filename, config_only, patterns_only, bank, pattern)

def configure(polyd, args_dict):
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

    for key,func in handlers.items():
        if key in args_dict:
            value = args_dict[key]
            if value is not None:
                func(value)
        else:
            raise PolyD_InvalidArgumentException(f"Unknown argument {key}")

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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-V", "--version", help=f"show {NAME}'s version number and exit", action="version",  version=f'%(prog)s {VERSION}')
    parser.add_argument("-l", "--list", help="list the MIDI interfaces and exit", action="store_true")
    parser.add_argument("-d", "--dump", help="dump the configuration to stdout", action="store_true")
    parser.add_argument("-s", "--save", help="save the configuration and patterns in file", default=None)
    parser.add_argument("-r", "--restore", help="write data from a file back to the instrument", default=None)
    parser.add_argument("-C", "--config_only", help="save/restore the configuration only", action="store_true")
    parser.add_argument("-P", "--patterns_only", help="restore the patterns only", action="store_true")
    parser.add_argument("-b", "--bank", help="the bank number of the saved or restored pattern", type=int, default=None)
    parser.add_argument("-p", "--pattern", help="the pattern number of the saved or restored pattern", type=int, default=None)
    parser.add_argument("--port", help="MIDI port name", default=None)
    parser.add_argument("--id", help="set the device id (0-127)", type=int, default=None)
    parser.add_argument("--rx", help="set MIDI rx channel (1-16)", type=int, default=None)
    parser.add_argument("--tx", help="set MIDI rx channel (1-16, All)", type=int, default=None)
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
    parser.add_argument("--sync_src", help=f"set the sync clock source ({get_range_string(PolyD_Config.SYNC_PORTS)})", default=None)
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

    port = 'POLY D'
    if args.port is not None:
        port = args.port

    with MidiConnection() as midi:
        in_id = first_or_default(midi.get_input_ids(), lambda n: is_polyd(port, n))
        out_id = first_or_default(midi.get_output_ids(), lambda n: is_polyd(port, n))
        if in_id is None or out_id is None:
            print("No Poly D found.")
            exit(1)
        if not midi.connect_write(out_id):
            print(f"Could not connect to MIDI device {out_id}.")
            exit(1)
        if not midi.connect_read(in_id):
            print(f"Could not connect to MIDI device {in_id}.")
            exit(1)

        polyd = PolyD(midi)
        version = polyd.get_version()
        if version[0] != 1 and version[1] != 1 and version[1] <= 3:
            print()
            print("Warning: This program is tested with firmware up to 1.1.3 only.")
            print("         It might not work as intended on other versions.")
            print()
            print("Poly-D reports firmware", version)
            print()
            exit(1)

        try:
            if args.save is not None:
                save(polyd, args.save, args.config_only, args.patterns_only, args.bank, args.pattern)

            if args.restore is not None:
                restore(polyd, args.restore, args.config_only, args.patterns_only, args.bank, args.pattern)

            args_dict = vars(args)
            configure(polyd, args_dict)

            if args.dump:
                config = polyd.get_config()
                dump(version, config)

        except MidiException as exc:
            print("Error:", exc.message)

if __name__ == "__main__":
    main()
