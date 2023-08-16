# Poly-D CLI

Poly-D CLI is a command line program that can be used to configure the behringer Poly-D synthesizer.

It offers the same settings as the official SYNTHTRIBE program, lacks a nice GUI, but runs on Linux as well.

The program was written and tested with a Poly-D with firmware version 1.1.0 only. If an instrument with another firmware version is connected, a warning is printed, and the program aborts.

Poly-D CLI uses the [Mido](https://github.com/mido/mido) library to talk to the synthesizer. This library needs to be installed separately like described on Mido's project page.

To connect to the synthesizer the first MIDI interface with `POLY D` in the name is used by the program. This means that configuring the Poly-D works only over the USB-MIDI connection.

## Usage

    usage: polyd-cli.py [-h] [-l] [-d] [--id ID] [--rx RX] [--tx TX] [--in_trans IN_TRANS] [--vel_on VEL_ON]
                        [--vel_off VEL_OFF] [--vel_curve VEL_CURVE] [--key_prio KEY_PRIO] [--multi_trig MULTI_TRIG]
                        [--pbend_range PBEND_RANGE] [--mod_range MOD_RANGE] [--mod_curve MOD_CURVE] [--note_zero NOTE_ZERO]
                        [--sync_rate SYNC_RATE] [--sync_src SYNC_SRC] [--local LOCAL] [--ext_pol EXT_POL]
                        [--acc_vel ACC_VEL] [--clock_out CLOCK_OUT] [--pbend_out PBEND_OUT] [--mod_out MOD_OUT]
                        [--key_out KEY_OUT] [--at_out AT_OUT] [--seq_out SEQ_OUT] [--arp_out ARP_OUT]

    options:
      -h, --help            show this help message and exit
      -l, --list            list the MIDI interfaces.
      -d, --dump            dumps the configuration.
      --id ID               set the device id (0-127)
      --rx RX               set MIDI rx channel (1-16)
      --tx TX               set MIDI rx channel (1-16)
      --in_trans IN_TRANS   set MIDI in transpose (-12-12)
      --vel_on VEL_ON       set the note on velocity (0-127)
      --vel_off VEL_OFF     set the note off velocity (0-127)
      --vel_curve VEL_CURVE
                            set the velocity curve ('soft', 'medium', 'hard' or 0-3)
      --key_prio KEY_PRIO   set the key priority ('low', 'high', 'last' or 0-3)
      --multi_trig MULTI_TRIG
                            set the multi trigger ('on', 'off' or 0-1)
      --pbend_range PBEND_RANGE
                            set the pitch bend range (0-24)
      --mod_range MOD_RANGE
                            set the mod wheel range ('20%', '50%', '100%', '200%', '300%' or 0-5)
      --mod_curve MOD_CURVE
                            set the modulation curve ('soft', 'medium', 'hard' or 0-3)
      --note_zero NOTE_ZERO
                            set the note at 0 CV (0-127)
      --sync_rate SYNC_RATE
                            set the sync clock rate ('1 PPS', '2 PPQ', '24 PPQ', '48 PPQ' or 0-4)
      --sync_src SYNC_SRC   set the sync clock source ('off', 'DIN', 'USB', 'both' or 0-4)
      --local LOCAL         set the local keyboard mode ('on', 'off' or 0-1)
      --ext_pol EXT_POL     set the external clock polarity ('falling', 'rising' or 0-2)
      --acc_vel ACC_VEL     set the accent velocity (0-127)
      --clock_out CLOCK_OUT
                            set the MIDI clock output ('off', 'DIN', 'USB', 'both' or 0-4)
      --pbend_out PBEND_OUT
                            set the pitch wheel MIDI output ('off', 'DIN', 'USB', 'both' or 0-4)
      --mod_out MOD_OUT     set the mod wheel MIDI output ('off', 'DIN', 'USB', 'both' or 0-4)
      --key_out KEY_OUT     set the keyboard MIDI output ('off', 'DIN', 'USB', 'both' or 0-4)
      --at_out AT_OUT       set the after touch MIDI output ('off', 'DIN', 'USB', 'both' or 0-4)
      --seq_out SEQ_OUT     set the sequencer MIDI output ('off', 'DIN', 'USB', 'both' or 0-4)
      --arp_out ARP_OUT     set the arpeggiator MIDI output ('off', 'DIN', 'USB', 'both' or 0-4)

Multiple commands can be given on one command line and all are performed. If a configuration dump is selected, it is performed after all commands that set values.

Text arguments, like for example for the velocity curve can be abbreviated. The first curve that contains the text, ignoring case and whitespace, is used in the case of velocity curves. 

## Poly-D SysEx Format

The SysEx commands used by `polyd-cli.py` can be found [here](polyd-sysex.md).
