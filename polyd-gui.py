#! /usr/bin/env python3

import kivy
kivy.require('2.3.0')

from kivy.config import Config
Config.set('graphics', 'width', str(450))
Config.set('graphics', 'height', str(880))
Config.set('graphics', 'resizable', False)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

NAME = 'polyd-gui'
VERSION = 1.0

from kivy.app import App

import argparse

from midiconnection import MidiConnection, MidiException
from polyd import PolyD, PolyD_Config, PolyD_Exception, PolyD_InvalidArgumentException
from polydguiview import PolyDGuiView

def first_or_default(arr, pred):
    return next(iter([x for x in arr if pred(x)]), None)

def is_polyd(searched_name, port_name):
    return searched_name in port_name

class PolyDGui(App):
    def __init__(self, polyd, **kwargs):
        self.polyd = polyd
        super().__init__(**kwargs)

    def build(self):
        self.title = "Poly D GUI"
        return PolyDGuiView(self.polyd)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-V", "--version", help=f"show {NAME}'s version number and exit", action="version", version=f'%(prog)s {VERSION}')
    parser.add_argument("-l", "--list", help="list the MIDI interfaces and exit", action="store_true")
    parser.add_argument("--port", help="MIDI port name", default=None)

    args = parser.parse_args()
    if args.list:
        ids = MidiConnection().get_ids()
        print()
        print("Ports:")
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

        PolyDGui(polyd).run()

if __name__ == "__main__":
    main()

