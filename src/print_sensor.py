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

        # #### FOR TRYING TO USE BITS (not strings)
        # # grab data from arduino (teensy)
        # # Reading 1 byte, followed by whatever
        # # is left in the read buffer, as 
        # # suggested by the developer of PySerial.
        # data = duino.readline(1)
        # data += duino.readline(duino.inWaiting())
        # if len(data) > 0:
        #     pass
        # else:
        #     print 'NO DATA DETECTED'

    except KeyboardInterrupt:
        import sys
        sys.exit()