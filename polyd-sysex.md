# Poly-D SysEx Format

## Command Format:

F0 00 20 32 00 01 0C did cmd nn ... F7

00 20 32 = Manufacturer SYS Id (Behringer GmbH)  
00 01 0C = Model Id (Poly-D)  
did = Device Id  
cmd = Command number  
nn ... = Arguments

## Sent to Poly-D

| Command         | Description               | Parameters                                      | Default |
| --------------- | ------------------------- | ----------------------------------------------- | ------- |
| 00 nn           | Set device id             | nn = Device Id (0-127), 0=Any                   | 0       |
| 02              |                           | Poly-D answers with Packet Type x03             |         |
| 08 00           | Request firmware version  | Poly-D answers with Packet Type x09             |         |
| 0E 00 nn mm     | Set MIDI channels         | nn = Out channel (0-16), 0=Any                  | 1       |
|                 |                           | mm = In Channel (0-16), 0=Any                   | 1       |
| 0F nn           | Set MIDI in transpose     | nn = Range -12 - +12 semitones (0-24)           | 12      |
| 10 nn mm pp     | Velocity info             | nn = Velocity On (0=dynamic, 1-127=Fixed)       | 0       |
|                 |                           | mm = Velocity Off (0=dynamic, 1-127=Fixed)      | 0       |
|                 |                           | pp = Curve (0=soft, 1=medium, 2=hard)           | 0       |
| 11 nn 00        | Pitch bend semi tones     | nn = Pitch bend semi tones (0-24)               | 12      |
| 12 nn           | Key priority              | nn = 0=Low, 1=High, 2=Last                      | 2       |
| 14 nn 00        | Set multi trigger         | nn = 0=Off, 1=On                                | 1       |
| 15 nn           | Modulation curve          | nn = 0=Soft, 1=Medium, 2=Hard                   | 0       |
| 16 nn           | Set note at 0V CV         | nn = MIDI note (0-127)                          | 24      |
| 17 nn           | MIDI clock out            | nn = 0=Off, 1=MIDI DIN, 2=MIDI USB, 3=Both      | 3       |
| 19 nn           | Polarity                  | nn = 0=Falling, 1=Rising                        | 1       |
| 1A nn           | Sync clock rate           | nn = 0=1 PPS, 1=2 PPQ, 2=24 PPQ, 3=48 PPQ       | 2       | 
| 1B nn           | Clock source              | nn = 0=Internal, 1=MIDI DIN, 2=MIDI USB, 3=Trig | 0       |
| 1C nn           | Set accent velocity       | nn = Accent Velocity (0-127)                    | 96      |
| 20 nn           | Modulation wheel range    | nn = 0=20%, 1=50%, 2=100%, 3=200%, 4=300%       | 2       |
| 21 nn           | Modulation wheel output   | nn = 0=Off, 1=MIDI DIN, 2=MIDI USB, 3=Both      | 3       |
| 22 nn           | Pitch wheel output        | nn = 0=Off, 1=MIDI DIN, 2=MIDI USB, 3=Both      | 3       |
| 23 nn           | Keyboard output           | nn = 0=Off, 1=MIDI DIN, 2=MIDI USB, 3=Both      | 3       |
| 24 nn           | Keyboard aftertouch       | nn = 0=Off, 1=MIDI DIN, 2=MIDI USB, 3=Both      | 3       |
| 25 nn           | Sequencer output          | nn = 0=Off, 1=MIDI DIN, 2=MIDI USB, 3=Both      | 3       |
| 26 nn           | Arpeggiator output        | nn = 0=Off, 1=MIDI DIN, 2=MIDI USB, 3=Both      | 3       |
| 2F nn           | Set local keyboard mode   | nn = 0=On, 1=Off                                | 1       |
| 75              | Request settings          | Poly-D answers with Packet Type 76              |         |
| 77 nn mm        | Request sequencer pattern | nn = Bank                                       |         |
|                 |                           | mm = Pattern                                    |         |
|                 |                           | Poly-D answers with Packet Type 78              |         |
| 7D              | Restore factory settings  |                                                 |         |

All commands setting a value on the Poly-D are answered with a packet of type 0x01 that tells if the action was successful or not.

## Received from Poly-D

| Packet data     | Description               |
| --------------- | ------------------------- |
| 01 00 nn        | nn = 0=Success, 5=Failure |
| 03 nn           |                           |
| 09 00 nn mm pp  | Firmware version nn.mm.pp |
| 76 nn ...       | Instrument settings       |
| 78 nn ...       | Sequencer pattern         |


### Instrument Settings

| Index | Value   | Description                 |
|------ | ------- | --------------------------- |
| 0     | 00      | Device Id                   |
| 1     | 00      | MIDI RX Channel             |
| 2     | 00      | MIDI TX Channel             |
| 3     | 0C      | MIDI In Transpose           |
| 4     | 00      | Key Velocity of Note On     |
| 5     | 00      | Key Velocity of Note Off    |
| 6     | 00      | Velocity Curve              |
| 7     | 02      | Key Priority                |
| 8     | 01      | Multi Trigger               |
| 9     | 0C      | Pitch Bend Range            |
| 10    | 02      | Modulation Wheel Range      |
| 11    | 00      | Modulation Curve            |
| 12    | 24      | Note at 0V CV               |
| 13    | 02      | Sync Clock Rate             |
| 14    | 00      | Sync Clock Source           |
| 15    | 01      | Local Keyboard Mode         |
| 16    | 01      | External Clock Polarity     |
| 17    | 60      | Accent Velocity             |
| 18    | 03      | MIDI Clock Output           |
| 19    | 03      | Pitch Wheel MIDI Output     |
| 20    | 03      | Mod Wheel MIDI Output       |
| 21    | 03      | Keyboard MIDI Output        |
| 22    | 03      | After Touch MIDI Output     |
| 23    | 03      | Sequencer MIDI Output       |
| 24    | 03      | Arpeggiator MIDI Output     |


### Sequencer Pattern

| Index | Value   | Description                 |
|------ | ------- | --------------------------- |
| 0     | 00      | Bank                        |
| 1     | 00      | Pattern                     |
| 2 ... | nn ...  |                             |
