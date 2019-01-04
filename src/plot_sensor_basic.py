'''Plotting without widgets, a single realtime plot.
'''

import sys
import serial
import numpy as np

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg


# must initialize Qt once
app = QtGui.QApplication([])

# open the plot
p = pg.plot()
p.setWindowTitle('live plot from serial')
curve = p.plot()

# initialize data structure
data = []
# limit the num of data points in the plot window
N_XPOINTS = 1000
# TODO: add timeout and baudrate args
duino = serial.Serial('/dev/cu.usbmodem52417201')


def update():
    try:
        global curve, data
        ser_str = duino.readline()
        ser_num = float(ser_str[:-2]) # drop the /r/n characters off the end
        print ser_num
        data.append(ser_num)
        # grab only last N points
        xdata = np.array(data[-N_XPOINTS:],dtype='float64')
        curve.setData(xdata)
        app.processEvents()
    except KeyboardInterrupt:
        print 'TEST within update function'
        app.quit()
        sys.exit()


timer = QtCore.QTimer()       # create a timer
timer.timeout.connect(update) # connect it to custom function
timer.start(0)                # call custom function every x seconds


if __name__ == '__main__':
    try:
        sys.exit(app.exec_())
    finally:
        print 'TEST at the end'
