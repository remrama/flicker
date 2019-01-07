'''
Only prints out the values read from duino.
This is only for simplest possible demonstration
of reading serial input from duino into python.
'''

import serial
import random

duino = serial.Serial('/dev/cu.usbmodem52417201')

while True:
    try:
        # grab data from arduino (teensy)
        # ser_str = duino.readline(duino.inWaiting())
        ser_str = duino.readline()
        sep = ser_str.split('\r')
        # sometimes 2 vals get sent
        vals = [ float(x) for x in sep if x.isalnum() ]
        for v in vals:
            print v
        #     # turn light on/off depending on value
        #     if v > 500:
        #         duino.write(bytes(1))
        #     else:
        #         duino.write(bytes(2))

        # # sending msg to duino
        # if random.choice([True,False]):
        #     duino.write(bytes(1)) # str would work python2 as well
        # else:
        #     duino.write(bytes(2))
        # # duino.write(b'test')
        # # serial.time.sleep(2)


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
        duino.close()
        serial.sys.exit()