
# trying to plot the sensor data live
# add sim flag if no duino present

from collections import deque
from itertools import islice

import sys
import time
import serial
import numpy as np

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg


# initialize variables
SERIAL_NAME = '/dev/cu.usbmodem52417201'
EXPORT_FNAME = './data.csv' #time.strftime('%Y%m%d%H%M%S')

N_XPOINTS = 1000 # limits data in plot window
REFRACTORY_SECS = 2 # time to go idle after a detected signal

# placeholder for timestamp of flicks
time_last_flick = 0

# open file with columns names
COLUMNS = ['stamp','data','flick']
with open(EXPORT_FNAME,'w') as newfile:
    newfile.write(','.join(COLUMNS))


# TODO: add timeout and baudrate args
try:
    duino = serial.Serial(SERIAL_NAME)
except serial.serialutil.SerialException:
    duino = None

# initialize list for holding data buffer
data = deque(maxlen=N_XPOINTS)
stamps = deque(maxlen=N_XPOINTS)
flicks = deque(maxlen=N_XPOINTS)


def grab_data():
    '''Grab data from the teensy by checking serial port.
    Doesn't return anything, just appends to existing lists.
    '''
    try:
        # receive from serial
        ser_str = duino.readline()
        # sometimes 2 vals get sent
        sep = ser_str.split('\r')
        vals = [ float(x) for x in sep if x.isalnum() ]
    except AttributeError: # since duino is None-type if no duino
        # simulate serial
        vals = [np.random.normal(500,100)] # as list to match receive_serial output

    stamp = time.time()

    ## TODO: currently this only includes the last
    ## _if_ multiple values come thu serial at once
    v = vals[-1]

    # update data buffer
    data.append(v)
    stamps.append(stamp)

    # check data for signal
    flick_found = look4signal()
    flicks.append(flick_found)

    # save
    saverow(outlist=[stamp,v,flick_found])


def saverow(outlist):
    '''Appends existing file.
    outlist : 1 value for each column
    '''
    with open(EXPORT_FNAME,'a') as outfile:
        outfile.write('\n'+','.join([ str(x) for x in outlist ]))




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
    if (time.time()-time_last_flick < REFRACTORY_SECS) or (len(data) < N_VALS):
        # skip soon after a found signal and beginning of stream 
        return 0
    else:
        data2search = list(islice(reversed(data),0,N_VALS)) # ugly slice bc of deque
        # check for signal
        # TEMP: check for heartbeat by looking for a "sharp rise",
        #       by looking for X datapoints mostly increasing
        # grab last 50 datapoints
        flick_found = np.mean(np.diff(data2search)>0) > .7
        return flick_found



# must initialize Qt once
app = QtGui.QApplication([])

# create a custom widget class

class MyWidg(QtGui.QWidget):
    '''will run until Xed out'''

    def __init__(self,n_xpoints=N_XPOINTS):
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
        self.plotw = pg.PlotWidget()

        # intialize some text in textspace
        self.listw.addItem(QtGui.QListWidgetItem('desired_updates_here'))

        # manage the widgets size and position
        grid = QtGui.QGridLayout()
        # add widgets to the grid/layout in their proper positions
        grid.addWidget(self.listw,0,0,2,1) # list widget goes on left, spanning 2 rows
        grid.addWidget(self.plotw,0,1,2,1) # plot goes on right side, spanning 2 rows

        # add this layout to the current class
        self.setLayout(grid)

        # instantiate the line to hold data on plot
        self.curve = self.plotw.plot()
        # ## TODO: consider this for speed (from examples)
        # # Use automatic downsampling and clipping to reduce the drawing load
        # self.plotw.setDownsampling(mode='peak')
        # self.plotw.setClipToView(True)

        # set y axis limits to prevent auto-updating
        self.plotw.setYRange(0,1023)
        self.plotw.setXRange(0,1000)
        self.plotw.setLabel('left','Value',units='V')
        self.plotw.getAxis('bottom').setTicks([])

        # choose size and title of window
        # self.setGeometry(300,300,300,300)
        self.setWindowTitle('flicker')
        
        # display the widget as a new window
        self.show()

        # open timer, which is what repeatedly runs the custom
        # function to check serial and plot incoming values
        self.timer = QtCore.QTimer() # create a timer
        self.timer.timeout.connect(self.update_plot) # connect it to custom function
        self.timer.start(0) # call custom function every x seconds

    def update_plot(self):
        grab_data()
        xdata = np.array(data,dtype='float64')
        self.curve.setData(xdata)
        if len(stamps) > 1:
            self.plotw.setTitle('{:.02f} fps'.format(1./np.mean(np.diff(stamps))))
        # app.processEvents() # force complete redraw for every plot
        # print heartbeat
        if flicks[-1]:
            # TODO: should this item be a QtGui.QListWidgetItem ??
            self.listw.addItem('{:.02f}, SACCADE'.format(time.time()-t0))
            # app.processEvents() # necessary??


    def closeEvent(self,event):
        '''this will execute upon closing window via "Xing out" window
        '''
        sys.exit()
        # self.SaveSettings()
        # # report_session()



if __name__ == '__main__':
    t0 = time.time() # for flicker display timestamps
    # define top-level (custom) widget
    w = MyWidg()
    sys.exit(app.exec_())

