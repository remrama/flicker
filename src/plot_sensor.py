
# trying to plot the sensor data live

import sys
import time
import serial
import numpy as np

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg


# initialize variables
SERIAL_NAME = '/dev/cu.usbmodem52417201'
EXPORT_FNAME = './data_{:s}.npy'.format(time.strftime('%Y%m%d%H%M%S'))

# TODO: add timeout and baudrate args
duino = serial.Serial(SERIAL_NAME)
# initialize data structures
data = []
stamps = []
hbeats = []


def look4signal():
    '''Detect heartbeat signal in an array.
    Always runs on the whole data list, which
    is constanly appended. So no input rn.
    RETURNS
        - 0 for no signal
        - 1 for found signal
        - .5 for found signal but soon after signal
    '''
    N_VALS = 100 # take the last N values from all data
    data2search = data[-N_VALS:]

    if len(data2search) < N_VALS:
        # skip beginning of stream
        return np.nan
    else:
        # check for signal
        # TEMP: check for heartbeat by looking for a "sharp rise",
        #       by looking for X datapoints mostly increasing
        # grab last 50 datapoints
        present = np.mean(np.diff(data2search)>0) > .5
        # choose output value
        if present:
            # if signal was recently detected, don't trigger
            # FOR NOW just see if there was a signal in recent samples
            if hbeats[-N_VALS:].count(1): # check for 1's
                outval = .5
            else:
                outval = 1
        else:
            outval = 0

        return outval



# must initialize Qt once
app = QtGui.QApplication([])

# create a custom widget class

class MyWidg(QtGui.QWidget):
    '''will run until Xed out'''

    def __init__(self,n_xpoints=1000):
        '''
        ARGS
        n_xpoints : limits data in plot window
        '''
        # run the regular widget initialization
        super(MyWidg,self).__init__()
        # run the custom initialization
        self.initUI()

        self.n_xpoints = n_xpoints

    def initUI(self):

        # create subwidgets?
        self.listw = QtGui.QListWidget()
        plotw = pg.PlotWidget()

        # intialize some text in textspace
        self.listw.addItem(QtGui.QListWidgetItem('desired_updates_here'))

        # manage the widgets size and position
        grid = QtGui.QGridLayout()
        # add widgets to the grid/layout in their proper positions
        grid.addWidget(self.listw,0,0,2,1) # list widget goes on left, spanning 2 rows
        grid.addWidget(plotw,0,1,2,1) # plot goes on right side, spanning 2 rows

        # add this layout to the current class
        self.setLayout(grid)

        # instantiate the line to hold data on plot
        self.curve = plotw.plot()
        # set y axis limits to prevent auto-updating
        plotw.setYRange(0,1023)

        # choose size and title of window
        # self.setGeometry(300,300,300,300)
        self.setWindowTitle('flicker')
        
        # display the widget as a new window
        self.show()

        # open timer, which is what repeatedly runs the custom
        # function to check serial and plot incoming values
        self.timer = QtCore.QTimer() # create a timer
        self.timer.timeout.connect(self.update_data) # connect it to custom function
        self.timer.start(0) # call custom function every x seconds

    def update_data(self):
        '''grab data from the teensy by checking serial port'''
        ser_str = duino.readline()
        # sometimes 2 vals get sent
        sep = ser_str.split('\r')
        vals = [ float(x) for x in sep if x.isalnum() ]
        stamp = time.time()
        for v in vals:
            # everything should be appended at once
            # print v
            data.append(v)
            stamps.append(stamp)
            # have to append a NaN on hbeats to keep the lengths
            # consistent then just replace it if it makes it there
            hbeats.append(np.nan)

        # grab only last N points
        xdata = np.array(data[-self.n_xpoints:],dtype='float64')
        self.curve.setData(xdata)
        app.processEvents()
        # ALSO check data for signal
        heartbeat = look4signal()
        # print heartbeat
        hbeats[-len(vals):] = np.repeat(heartbeat,len(vals))
        if heartbeat == 1:
            # TODO: should this item be a QtGui.QListWidgetItem ??
            self.listw.addItem('{:.02f}, HEARTBEAT'.format(time.time()-t0))
            app.processEvents() # necessary??

    def save(self):
        # save as numpy binary
        np.save(EXPORT_FNAME,np.column_stack([stamps,data,hbeats]))
        print 'data saved'

    def closeEvent(self,event):
        '''this will execute upon closing window via "Xing out" window
        '''
        self.save()
        sys.exit()
        # self.SaveSettings()
        # # report_session()



if __name__ == '__main__':
    t0 = time.time() # for flicker display timestamps
    # define top-level (custom) widget
    w = MyWidg()
    sys.exit(app.exec_())

