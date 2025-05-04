import os
import re
import queue

import mido

class MidiException(Exception):
    def __init__(self, message):
        self.message = message

class MidiConnection(object):
    def __init__(self):
        self.__queue = queue.Queue()
        self.__input = None
        self.__output = None
        self.read_connected = False
        self.write_connected = False

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.disconnect()
   
    @staticmethod
    def __get_device_names(names):
        result = set()
        for name in names:
            #print(name)
            m = re.match(r"^[^:]+:(.*)\s+\d+:\d+$", name)
            if m is None:
                result.add(name)
            else:
                result.add(m.group(1))
        return sorted(result, key=lambda x: x.lower())

    @staticmethod
    def get_ids():
        return MidiConnection.__get_device_names(mido.get_input_names() + mido.get_output_names())

    @staticmethod
    def get_input_ids():
        return MidiConnection.__get_device_names(mido.get_input_names())

    @staticmethod
    def get_output_ids():
        return MidiConnection.__get_device_names(mido.get_output_names())

    def connect(self, in_name=None, out_name=None, callback=None):
        self.connect_write(out_name)
        self.connect_read(in_name)
        return self.read_connected and self.write_connected

    def connect_write(self, out_name):
        if self.write_connected:
            self.disconnect_write()
        self.__output = mido.open_output(name=out_name, autoreset=True)
        self.write_connected = True
        return self.write_connected

    def connect_read(self, in_name=None):
        if self.read_connected:
            self.disconnect_read()
        self.__input = mido.open_input(name=in_name, callback=self.__input_callback)
        self.read_connected = True
        return self.read_connected

    def disconnect(self):
        self.disconnect_write()
        self.disconnect_read()

    def disconnect_write(self):
        if self.__output is not None:
            self.__output.close()
        self.__output = None
        self.write_connected = False

    def disconnect_read(self):
        if self.__input is not None:
            self.__input.close()
        self.__input = None
        self.read_connected = False

    def write_short(self, *args):
        """ Sends a MIDI message. """
        self.__output.send(mido.Message.from_bytes(args))

    def write(self, data):
        """ Sends a MIDI message. """
        msg = mido.Message.from_bytes(data)
        #print(msg.hex())
        self.__output.send(msg)

    def read(self):
        """ Reads the oldest MIDI message from the queue. 
            After 5 seconds an Empty"""
        try:
            return self.__queue.get(timeout=5)
        except:
            raise MidiException("Timeout while waiting for answer from MIDI device.")

    def send_sysex(self, filename):
        """ Sends the contents of a sysex file. """
        if not os.path.isfile(filename):
            return
        for message in mido.read_syx_file(filename):
            self.__output.send(message)

    def sysex_communicate(self, message_data):
        """ Sends a sysex question and waits for the answer. """
        self.write(message_data)
        while True:
            msg = self.read()
            if msg.type == 'sysex':
                return msg

    def panic(self):
        self.__output.panic()

    def __input_callback(self, msg):
        #print(msg)
        self.__queue.put(msg)
        while self.__queue.qsize() > 100:
            self.__queue.get()