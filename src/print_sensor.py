'''
Only prints out the values read from duino.
This is only for simplest possible demonstration
of reading serial input from duino into python.
'''

import serial

duino = serial.Serial('/dev/cu.usbmodem52417201')

while True:
    try:
        # grab data from arduino (teensy)
        ser_str = duino.readline()
        sep = ser_str.split('\r')
        # sometimes 2 vals get sent
        vals = [ float(x) for x in sep if x.isalnum() ]
        for v in vals:
            print v

    except KeyboardInterrupt:
        import sys
        sys.exit()