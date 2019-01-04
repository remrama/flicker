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
        # Reading 1 byte, followed by whatever
        # is left in the read buffer, as 
        # suggested by the developer of PySerial.
        data = duino.readline(1)
        data += duino.readline(duino.inWaiting())

        if len(data) > 0:
            pass
        else:
            print 'NO DATA DETECTED'


    except KeyboardInterrupt:
        duino.close()
        import sys
        sys.exit()