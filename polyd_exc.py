from midiconnection import MidiException

class PolyD_Exception(MidiException):
    def __init__(self, message):
        super().__init__(message)

class PolyD_InvalidArgumentException(PolyD_Exception):
    def __init__(self, message):
        super().__init__(message)

class PolyD_MidiException(PolyD_Exception):
    def __init__(self, message):
        super().__init__(message)
